from telethon import TelegramClient, events, sync
import json
import time
import requests
import re
from datetime import datetime, timezone, timedelta
import httpx
import asyncio

tz = timezone(timedelta(hours=+8))
config = json.load(open('config.json'))
client = TelegramClient('session_name', config["api_id"], config["api_hash"])
client.start()

async def sendToWechat(text):
    try:
        params = {
            "corpid": config['corpid'],
            "corpsecret": config['corpsecret']
        }
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params = params)
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
        async with httpx.AsyncClient() as client:
            r = await client.post(url, params = params, json = data)
    except Exception as e:
        print(e)
        pass 

async def sendToTrade(text):
    try:
        async with httpx.AsyncClient() as client:
            await client.post("http://localhost:5000", json={"data": text})
    except Exception as e:
        print(e)
        pass

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
    if publishTime != "":
        text += publishTime + "\n"
    print(datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S"))
    print(text)

    task1 = asyncio.create_task(sendToTrade(text))
    task2 = asyncio.create_task(sendToWechat(text))
    await task1
    await task2


client.run_until_disconnected()
