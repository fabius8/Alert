from bs4 import BeautifulSoup
import re
import time
import requests
import json
from datetime import datetime, timezone, timedelta
import sys

if len(sys.argv) == 2:
    site = sys.argv[1]
else:
    site = "binance.com"

tz = timezone(timedelta(hours=+8))
config = json.load(open('config.json'))
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
        headers = {
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        params = {
            "random": str(int(time.time()))
        }
        binance_announcement_site = "https://www." + site + "/en/support/announcement"
        r = requests.get(binance_announcement_site, timeout=5, params=params, headers=headers)
        #print(r.request.headers)
    except requests.exceptions.RequestException as e:
        print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"), e, errCount)
        errCount += 1
        return {}
    soup = BeautifulSoup(r.text, "html.parser")
    data = soup.find(id="__APP_DATA")
    catalogs = json.loads(data.string)["routeProps"]["42b1"]["catalogs"]
    # test
    # print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"))
    # for i in range(len(catalogs)):
    #     print(catalogs[i]['articles'][0])
    # print("\n")

    for i in range(len(catalogs)):
        catalogs[i]["icon"] = ""

    if binancePreviousCatalogs == None:
        binancePreviousCatalogs = catalogs
        
    for i in range(len(catalogs)):
        if catalogs[i]['articles'][0] not in binancePreviousCatalogs[i]['articles']:
            newArticles.append({"catalogName": catalogs[i]["catalogName"], "title": catalogs[i]['articles'][0]['title']})
            binancePreviousCatalogs = catalogs
            break
    return newArticles


if __name__ == "__main__":
    print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"), site, "Start...")
    while True:
        try:
            alert = binanceAlert()
            for i in alert:
                text = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + "\n"
                text += i['catalogName'] + ":" + "\n" + i['title'] + "\n"
                print(text)
                try:
                    requests.post("http://localhost:5000", json={"data": i['title']})
                except Exception as err:
                    text += str(err)
                    pass
                sendmsg(text)
                break
        except Exception as err:
            text += str(err)
            print(text)
            #sendmsg(text)

        time.sleep(5)
