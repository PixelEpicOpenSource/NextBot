import argparse
import nonebot.adapters.onebot.v11
from nonebot import on_message, on_notice, on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.rule import to_me
import time
from nonebot.permission import SUPERUSER


localstorage = {"messages": {}, "recalls": []}

# 缓存十分钟内接收的所有消息
achieve_message = on_message()


@achieve_message.handle()
async def handle_message(event: nonebot.adapters.onebot.v11.Event):
    localstorage['messages'][str(event.message_id)] = event
    for each in localstorage['messages']:
        # print(localstorage['messages'][each])
        if(time.time() - localstorage['messages'][each].time >= 60*10):  # 10 min
            del localstorage['messages'][each]
            print("remove", each)


#捕捉notice事件 friend_recall和group_recall
recall = on_notice()


@recall.handle()
async def handle_recall(event: nonebot.adapters.onebot.v11.Event):
    if(event.notice_type == "friend_recall" or event.notice_type == "group_recall"):
        try:
            localstorage['recalls'].append(
                {"achieved": True,
                 "time": event.time,
                 "user_id": event.user_id,
                 "user_name": localstorage['messages'][str(event.message_id)].sender.nickname,
                 "message_id": event.message_id,
                 "message_data": localstorage['messages'][str(event.message_id)]})
        except:#防止撤回了未缓存的消息导致报错
            localstorage['recalls'].append(
                {"achieved": False,
                 "time": event.time,
                 "user_id": event.user_id,
                 "message_id": event.message_id})

get_recalls = on_command("recalls", rule=to_me(), aliases={
    "撤回"},permission=SUPERUSER)


@get_recalls.handle()
async def send_recalls(args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    print(localstorage)
    if(plain_text == ""):
        reply_str = "查询撤回消息\n已缓存消息" + \
            str(len(localstorage['messages']))+"条\n已记录撤回" + \
            str(len(localstorage['recalls']))+"条\n\n"
        num = 1
        for each in localstorage['recalls']:
            if(each['achieved'] == True):
                reply_str += str(num)+". "+str(each['user_name'])+"("+str(
                    each['user_id'])+") "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(each["message_data"].time)))+"\n"+each["message_data"].raw_message
            else:
                reply_str += str(num)+". <无法查询>("+str(
                    each['user_id'])+")"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(each["time"])))
            reply_str += "\n"
            num += 1
        reply_str += '\n使用"/撤回 [id]"查看消息原文\n使用"/撤回 clear"清空记录'
        await get_recalls.send(reply_str)
    elif(plain_text == "clear"):
        await get_recalls.send("已清空")
    else:
        try:
            msg_data = localstorage["recalls"][int(plain_text)-1]
            await get_recalls.send("发送者: "+msg_data['user_name']+"("+str(msg_data['user_id'])+")\n发送时间: "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(msg_data['time'])))+"\n撤回时间: "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(msg_data["message_data"].time))))
            await get_recalls.send(msg_data['message_data'].message)
        except:
            await get_recalls.send("无法查询"+plain_text+"，请检查输入")
