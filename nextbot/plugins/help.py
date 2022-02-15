from nonebot import on_command, CommandSession
from nonebot.message import unescape
import os
import random
import time
import requests
import json
#from rimo_storage import 超dict

localstorage = {}  # 超dict('./luck')


def getSeed():
    global localstorage
    now = time.strftime("%Y-%m-%d", time.localtime())
    if('date' not in localstorage.keys() or now != localstorage['date']):
        print("generate seed")
        localstorage['seed'] = random.randint(1, 100)
        localstorage['date'] = now
        localstorage['user'] = {}
    print(localstorage['seed'], localstorage['date'])
    return localstorage['seed']


getSeed()


def getAttempt(user_id):
    user_id = str(user_id)
    global localstorage
    if(user_id not in localstorage['user']):
        localstorage['user'][user_id] = 1
    else:
        localstorage['user'][user_id] += 1
    return(localstorage['user'][user_id])


@on_command('help', aliases=('帮助'))
async def help(session: CommandSession):
    await session.send('''= NextBot =
    https://github.com/PixelEpicOpenSource/NextBot
    Usage:
        签到
        点歌 [music name]''')


@on_command('sign', aliases=('签到', '每日签到'))
async def sign(session: CommandSession):
    user_id = session.event['user_id']
    jrrp = (user_id // getSeed()) % 101
    if (getAttempt(user_id) <= 1):
        await session.send("签到成功(≧▽≦)！你今天的人品是："+str(jrrp))
    else:
        await session.send("你知道吗，反复签到可是要掉脑袋的(๑•﹏•)")


@on_command('sudo', permission=lambda s: s.is_superuser)
async def sudo(session: CommandSession):
    try:
        cmdout = os.popen(session.current_arg_text.strip()).read()
    except:
        cmdout = "[ERROR]"
    print(cmdout, type(cmdout))
    await session.send(cmdout)


@on_command('music', aliases=('点歌', '我要听'), only_to_me=False)
async def music(session: CommandSession):
    re = json.loads(requests.get(
        "http://localhost:3000/cloudsearch?limit=1&keywords="+session.current_arg_text.strip()).text)['result']['songs'][0]['id']
    await session.send(unescape("[CQ:music,type=163,id="+str(re)+"]"))
