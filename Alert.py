from bs4 import BeautifulSoup
import re
import time
import requests
import json
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=+8))

config = json.load(open('config.json'))
binance_announcement_site = "https://www.binancezh.top/zh-CN/support/announcement"
binancePreviousCatalogs = None
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
        "agentid" : config['agentid'],
        "text" : {
            "content" : text
        }
    }
    r = requests.post(url, params = params, json = data)

def binanceAlert():
    global binancePreviousCatalogs
    global errCount
    newArticles = []

    try:
        r = requests.get(binance_announcement_site, timeout=5)
    except requests.exceptions.RequestException as e:
        print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"), e, errCount)
        errCount += 1
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    data = soup.find(id="__APP_DATA")
    catalogs = json.loads(data.string)["routeProps"]["42b1"]["catalogs"]

    for i in range(len(catalogs)):
        catalogs[i]["icon"] = ""

    if binancePreviousCatalogs == None:
        binancePreviousCatalogs = catalogs
    elif binancePreviousCatalogs != catalogs:
        print(binancePreviousCatalogs)
        print(catalogs)
        for i in range(len(catalogs)):
            if catalogs[i]['articles'][0] not in binancePreviousCatalogs[i]['articles']:
                newArticles.append({"catalogName": catalogs[i]["catalogName"], "title": catalogs[i]['articles'][0]['title']})
        binancePreviousCatalogs = catalogs
    return newArticles


if __name__ == "__main__":
    print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"), "Start...")
    while True:
        text = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + "\n"
        try:
            alert = binanceAlert()
            for i in alert:
                text += i['catalogName'] + ":" + i['title'] + "\n"
                print(text)
                sendmsg(text)
        except Exception as err:
                text += err
                print(text)
                sendmsg(text)

        time.sleep(1)
