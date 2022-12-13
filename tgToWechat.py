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

async def sendToWechat(text, corpid, corpsecret, agentid):
    try:
        params = {
            "corpid": corpid,
            "corpsecret": corpsecret
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
            "agentid" : agentid,
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
        mm = event.message.message
        if "twitter" in mm:
            print("skip twitter")
            return
        mm = mm.split("\n")
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

    if "币安\n" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["binancealert"]["corpid"], config["binancealert"]["corpsecret"], config["binancealert"]["agentid"]))
    elif "Gate.io" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["gatealert"]["corpid"], config["gatealert"]["corpsecret"], config["gatealert"]["agentid"]))
    elif "mexc.com" in text or "MXC.io" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["mexcalert"]["corpid"], config["mexcalert"]["corpsecret"], config["mexcalert"]["agentid"]))
    elif "OKEX.COM" in text or "OKEX" in text or "OKX" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["okexalert"]["corpid"], config["okexalert"]["corpsecret"], config["okexalert"]["agentid"]))
    elif "火币" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["huobialert"]["corpid"], config["huobialert"]["corpsecret"], config["huobialert"]["agentid"]))
    elif "coinbase" in text or "CoinBase" in text or "coinBase" in text or "Coinbase" in text or "COINBASE" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["coinbasealert"]["corpid"], config["coinbasealert"]["corpsecret"], config["coinbasealert"]["agentid"]))
    elif "ftx\n" in text or "FTX\n" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["ftxalert"]["corpid"], config["ftxalert"]["corpsecret"], config["ftxalert"]["agentid"]))
    elif "kucoin" in text:
        task2 = asyncio.create_task(sendToWechat(text, config["kucoinalert"]["corpid"], config["kucoinalert"]["corpsecret"], config["kucoinalert"]["agentid"]))
    else:
        task2 = asyncio.create_task(sendToWechat(text, config["allalert"]["corpid"], config["allalert"]["corpsecret"], config["allalert"]["agentid"]))

    await task1
    await task2


client.run_until_disconnected()
