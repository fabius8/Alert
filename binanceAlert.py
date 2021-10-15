from bs4 import BeautifulSoup
import re
import time
import requests
import json
from datetime import datetime

config = json.load(open('config.json'))
binance_announcement_site = "https://www.binance.com/zh-CN/support/announcement"
previousCatalogs = None
errCount = 0

def sendmsg(text):
    params = {
        "corpid": config['corpid'],
        "corpsecret": config['corpsecret']
    }
    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    r = requests.get(url, params = params)
    access_token = r.json()["access_token"]
    url = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
    params = {
        "access_token": access_token
    }
    data = {
        "touser": "@all",
        "msgtype" : "text",
        "agentid" : 1000002,
        "text" : {
            "content" : text
        }
    }
    r = requests.post(url, params = params, json = data)

def binanceAlert():
    global previousCatalogs
    global errCount
    newArticles = []

    try:
        r = requests.get(binance_announcement_site, timeout=5)
    except requests.exceptions.RequestException as e:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), e, errCount)
        errCount += 1
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    data = soup.find(id="__APP_DATA")
    catalogs = json.loads(data.string)["routeProps"]["42b1"]["catalogs"]

    if previousCatalogs == None:
        previousCatalogs = catalogs
    elif previousCatalogs != catalogs:
        for i in range(len(catalogs)):
            if previousCatalogs[i]['articles'][0] != catalogs[i]['articles'][0]:
                newArticles.append({"catalogName": catalogs[i]["catalogName"], "title": catalogs[i]['articles'][0]['title']})
        previousCatalogs = catalogs
    return newArticles

if __name__ == "__main__":
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Start...")
    while True:
        alert = binanceAlert()
        text = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        for i in alert:
            text += i['catalogName'] + ":" + i['title'] + "\n"
            print(text)
            sendmsg(text)
            
        time.sleep(1)
