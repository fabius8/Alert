from telethon import TelegramClient, events, sync
import json
import time
import requests
import re
import datetime

config = json.load(open('config.json'))
client = TelegramClient('session_name', config["api_id"], config["api_hash"])
client.start()

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

@client.on(events.NewMessage(chats=1388754506))
async def handler(event):
    text = ""
    try:
        mm = event.message.message.split("\n")
    except Exception as e:
        print(e)
        pass
    publishTime = ""
    for i in mm:
        if "发布时间" in i or "publish time" in i:
            publishTime = i
        elif "-----" in i:
            continue
        else:
            text += i + "\n"
    if publish != "":
        text += publishTime + "\n"
    print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"))
    print(text)

    try:
        requests.post("http://localhost:5000", json={"data": text})
    except Exception as e:
        print(e)
        pass

    try:
        sendmsg(text)
    except Exception as e:
        print(e)
        pass 

client.run_until_disconnected()
