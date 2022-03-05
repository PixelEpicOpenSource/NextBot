import json

import nonebot.adapters.onebot.v11.message
import requests
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.rule import to_me

music = on_command("music", rule=to_me(), aliases={
    "点歌"})


@music.handle()
async def music_handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("name", args)


@music.got("name", prompt="请输入歌名或网易云歌曲ID")
async def music_handle(name: str = ArgPlainText("name")):
    music_info = await get_music(name)
    await music.send(music_info)


async def get_music(name: str) -> str:
    try:
        music_id = int(json.loads(requests.get(
            "http://localhost:3000/cloudsearch?limit=1&keywords="+name).text)['result']['songs'][0]['id'])
        # "[CQ:music,type=163,id="+str(re)+"]"
        return nonebot.adapters.onebot.v11.message.MessageSegment.music(type_="163", id_=music_id)
    except:
        return "搜索不到"+name+"，请检查拼写"


lyric = on_command("lyric", rule=to_me(), aliases={
    "歌词"})


@lyric.handle()
async def lyric_handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("name", args)


@lyric.got("name", prompt="请输入歌名或网易云歌曲ID")
async def lyric_handle(name: str = ArgPlainText("name")):
    music_lyric = await get_lyric(name)
    await music.send(music_lyric)


async def get_lyric(name: str) -> str:
    try:
        music_id = int(json.loads(requests.get(
            "http://localhost:3000/cloudsearch?limit=1&keywords="+name).text)['result']['songs'][0]['id'])
        # "[CQ:music,type=163,id="+str(re)+"]"
        music_lyric = json.loads(requests.get(
            "http://localhost:3000/lyric?id="+str(music_id)).text)['lrc']['lyric']
        return music_lyric
    except:
        return "搜索不到"+name+"，请检查拼写"
