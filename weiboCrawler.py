# -*- coding: utf8 -*-
"""
Created on Wed Apr 06 09:46:31 2016

@author: tanhe
"""

import requests
from bs4 import BeautifulSoup
import os,sys
import subprocess
import time
from urllib import quote
import getopt

reload(sys)
sys.setdefaultencoding("utf8")

if sys.platform.find('darwin') >= 0:
    code = "utf8"
elif sys.platform.find('linux') >= 0:
    code = "utf8"
else:
    code = "gbk"


try:
    opts, args = getopt.getopt(sys.argv[1:], "hrcaw:u:", ["help", "repost","comment","userID=","attitude","weiboID="])
except getopt.GetoptError:
    print u"参数不正确".encode(code)

url = "http://login.weibo.cn/login/?"
repost_url = "http://weibo.cn/repost/"
comment_url = "http://weibo.cn/comment/"
attitude_url = "http://weibo.cn/attitude/"
user_url = "http://weibo.cn/"
CAPTCHAPath = os.path.join(os.getcwd(), 'CAPTCHA.jpg')
param = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"}
s = requests.session()

def usage():
    print u'''抓转发: python weiboCrawler.py -w 微博ID -r;
抓评论: python weiboCrawler.py -w 微博ID -c;
抓点赞: python weiboCrawler.py -w 微博ID -a;
抓用户: python weiboCrawler.py -u 用户ID;'''.encode(code)
    
    

def login():
    username = raw_input(u"请输入用户名：".encode(code))
    password = raw_input(u"请输入密码：".encode(code))
    req = requests.get(url,headers=param)
    soup = BeautifulSoup(req.text,"html.parser")
    img_url = soup.find("img").get("src")
    pass_name = soup.find("input",{"type":"password"}).get("name")
    backURL = soup.find("input",{"name":"backURL"}).get("value")
    backTitle = soup.find("input",{"name":"backTitle"}).get("value")
    vk = soup.find("input",{"name":"vk"}).get("value")
    capId = soup.find("input",{"name":"capId"}).get("value")
    submit = soup.find("input",{"name":"submit"}).get("value")
    
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        with open(CAPTCHAPath, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    time.sleep(1)
    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', CAPTCHAPath])
    elif sys.platform.find('linux') >= 0:
        subprocess.call(['xdg-open', CAPTCHAPath])
    else:
        os.startfile(CAPTCHAPath)
    CAPTCHA = raw_input(u"请输入验证码:".encode(code))
    
    data = {"mobile":username,pass_name:password,"code":quote(CAPTCHA.decode(code).encode("utf8")),"remember":"on","backURL":backURL,
            "backTitle":backTitle,"vk":vk,"capId":capId,"submit":submit}
    
    req = s.post("http://login.weibo.cn/login/?",data=data,headers=param)
    soup = BeautifulSoup(req.text,"html.parser")
    if soup.find("div",{"class":"me"}) == None:
        print u"-----------登录成功---------".encode(code)
    else:
        print u"-----------验证码或用户名或密码不对，请重新登录！-----------".encode(code)
        login()

def getPageNum(url):
    req = s.get(url+"?page=1")
    soup = BeautifulSoup(req.text,"html.parser")
    try:
        pageNum = soup.find("input",{"name":"mp"}).get("value")
    except:
        pageNum = 1
    return int(pageNum)
 
def parseC(url,outfile):
    req = s.get(url,headers=param)
    soup = BeautifulSoup(req.text,"html.parser",from_encoding="utf8")
    contents = soup.find_all("div",{"class":"c"})
    content = ""
    time = ""
    for c in contents:
        try:
            id = c.get("id")
            user = c.find("a").text
            user_url = c.find("a").get("href")
            content = c.find("span",{"class":"ctt"}).text
            time = c.find("span",{"class":"ct"}).text.strip()
            print id,user.encode(code,"ignore"),content.encode(code,"ignore")
            line = "%s\t%s\t%s\t%s\t%s\n" %(id,user.encode("utf8"),user_url,content.encode("utf8"),time.encode("utf8"))
            outfile.write(line)
        except Exception,e:
            #print e
            pass

 
def parseR(url,outfile):
    req = s.get(url,headers=param)
    soup = BeautifulSoup(req.text,"html.parser",from_encoding="utf8")
    contents = soup.find_all("div",{"class":"c"})
    for c in contents:
        try:
            user = c.find("a").text
            user_url = c.find("a").get("href")
            texts = c.find_all(text=True)
            texts = [t.strip() for t in texts if t.strip() != ""]
            content = "".join(texts[1:-2])
            time = c.find("span",{"class":"ct"}).text.strip()
            print user.encode(code,"ignore"),content.encode(code,"ignore")
            line = "%s\t%s\t%s\t%s\n" %(user,user_url,content.encode("utf8","ignore"),time.encode("utf8","ignore"))
            outfile.write(line)
        except Exception,e:
            #print e
            pass

def parseA(url,outfile):
    req = s.get(url,headers=param)
    soup = BeautifulSoup(req.text,"html.parser",from_encoding="utf8")
    contents = soup.find_all("div",{"class":"c"})
    for c in contents:
        try:
            user = c.find("a").text
            user_url = c.find("a").get("href")
            time = c.find("span",{"class":"ct"}).text.strip()
            print user.encode(code,"ignore")
            line = "%s\t%s\t%s\n" %(user.encode("utf8","ignore"),user_url,time.encode("utf8","ignore"))
            outfile.write(line)
        except Exception,e:
            #print e
            pass
            
def parse(url,outfile):
    content = ""
    like = ""
    repost = ""
    comment = ""
    time = ""
    ori_user = ""
    ori_userID = ""
    ori_text = ""
    ori_like = ""
    ori_repost = ""
    ori_comment = ""

    req = s.get(url,headers=param)
    soup = BeautifulSoup(req.text,"html.parser",from_encoding="utf8")
    contents = soup.find_all("div",{"class":"c"})
    for c in contents:
        try:
            id = c.get("id")
            divs = c.find_all("div")
            if divs[-1].find("span",{"class":"ct"}).find("a"):
                texts = divs[-1].find_all(text=True)
                texts = [t.strip() for t in texts if t.strip() != ""]
                content = "".join(texts[:-6])
                like = texts[-6]
                repost = texts[-5]
                comment  = texts[-4]
                time = divs[-1].find("span",{"class":"ct"}).find_all(text=True) 
            else:
                texts = divs[-1].find_all(text=True)
                texts = [t.strip() for t in texts if t.strip() != ""]
                content = "".join(texts[:-5])
                like = texts[-5]
                repost = texts[-4]
                comment  = texts[-3]
                time = texts[-1]
            if len(divs) == 3:  
                ori_user = divs[0].find("span",{"class":"cmt"}).find("a").text
                ori_userID = divs[0].find("span",{"class":"cmt"}).find("a").get("href")
                ori_text = divs[0].find("span",{"class":"ctt"}).text
                spans = divs[1].find_all("span",{"class":"cmt"})
                ori_like = spans[0].text
                ori_repost = spans[1].text
                ori_comment = divs[1].find("a",{"class":"cc"}).text           
            print id,content.encode(code,"ignore")
            line = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %(id,content.encode("utf8"),\
            like.encode("utf8"), repost.encode("utf8"), comment.encode("utf8"), time.encode("utf8"),\
            ori_user.encode("utf8"), ori_userID, ori_text.encode("utf8"), ori_like.encode("utf8")\
            , ori_repost.encode("utf8"),  ori_comment.encode("utf8"))
            outfile.write(line)
        except Exception,e:
            #print e
            pass
            
    
if __name__ == "__main__":
    
    weiboID = ""
    userID = ""
#    login()
#    url = "http://weibo.cn/comment/DpFYxkHW5"
#    pgNum = getPageNum(url)
#    fileName = url.split("/")[-1]+"_"+"repost"
#    filePath = os.path.join(os.getcwd(), fileName+".txt")
#    with open(filePath,"a") as outfile:
#        for i in range(1,pgNum):
#            pg_url = url + "?page=%d" %i
#            parseC(pg_url,outfile)
#            time.sleep(2) 
    
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
            exit()
        if o in ("-u","--userID"):
            userID = a
            if userID == "":
                print u"UserID不能为空".encode(code)
                exit()
            else:
                login()
                url = user_url + userID
                pgNum = getPageNum(url)
                fileName = "User"+"_"+url.split("/")[-1]
                filePath = os.path.join(os.getcwd(), fileName+".txt")
                with open(filePath,"a") as outfile:
                    for i in range(1,pgNum):
                        pg_url = url + "?page=%d" %i
                        parse(pg_url,outfile)
                        time.sleep(2)  
        if o in ("-w","--weiboID"):
            if a == "":
                print u"weiboID不能为空".encode(code)
                exit()
            else:
                weiboID = a
                print u'-----------微博登录-----------'.encode(code)
                login()
        if o in ("-r","--repost"):
            if weiboID == "":
                print u"weiboID不能为空".encode(code)
                exit()
            else:
                url = repost_url + weiboID
                pgNum = getPageNum(url)
                fileName = url.split("/")[-1]+"_"+"repost"
                filePath = os.path.join(os.getcwd(), fileName+".txt")
                with open(filePath,"a") as outfile:
                    for i in range(1,pgNum):
                        pg_url = url + "?page=%d" %i
                        parseR(pg_url,outfile)
                        time.sleep(2)            
        if o in ("-c","--comment"):
            if weiboID == "":
                print u"weiboID不能为空".encode(code)
                exit()
            else:
                url = comment_url + weiboID
                pgNum = getPageNum(url)
                fileName = url.split("/")[-1]+"_"+"comment"
                filePath = os.path.join(os.getcwd(), fileName+".txt")
                with open(filePath,"a") as outfile:
                    for i in range(1,pgNum):
                        pg_url = url + "?page=%d" %i
                        parseC(pg_url,outfile)
                        time.sleep(2)  
        if o in ("-a","--attitude"):
            if weiboID == "":
                print u"weiboID不能为空".encode(code)
                exit()
            else:
                url = attitude_url + weiboID
                pgNum = getPageNum(url)
                fileName = url.split("/")[-1]+"_"+"attitude"
                filePath = os.path.join(os.getcwd(), fileName+".txt")
                with open(filePath,"a") as outfile:
                    for i in range(1,pgNum):
                        pg_url = url + "?page=%d" %i
                        parseA(pg_url,outfile)
                        time.sleep(2) 
    
   
    
