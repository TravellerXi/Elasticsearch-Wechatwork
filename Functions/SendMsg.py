#!/usr/bin/env python3
# coding:utf-8
"""
微信消息发送模板。
目前用到的函数：SendTextToApp，SendMarkDownToApp
"""

import requests
import json
from Functions.CorpInfo import *


def SendTextToApp(UserId,Content):
    '''
        发送纯文本信息
        UserId：String
        Content:String
    '''
    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    access_token = (GetResponse['access_token'])
    rawdata = {
        "touser" : UserId,
        "msgtype" : "text",
        "agentid" : AgentID,
        "text" : {
            "content" : Content
            },
        "safe":0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
}
    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    return 0



def SendMarkDownToApp(UserId, Content):
    """
    UserID:str
    Content:str
    发送Zabbix更新或者关闭卡片，Markdown语言支持
    """
    GetResponse = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + CorpID + "&corpsecret=" + CorpSecret,
        proxies=proxy).json()
    access_token = (GetResponse['access_token'])

    rawdata = {
        "touser": UserId,
        "msgtype": "markdown",
        "agentid": AgentID,
        "markdown": {
            "content": Content
        },
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    requests.post(post_url, json.dumps(rawdata), proxies=proxy)
    return 0


def UpdateTaskCardToApp(UserId,TaskID,clicked_key):
    """
    更新任务卡片，当用户点击确认处理时，调用处理程序后，会再调用此函数。
    """
    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    access_token = (GetResponse['access_token'])
    rawdata = {
        "userids" : [UserId],
        "agentid" : AgentID,
        "task_id": TaskID,
        "clicked_key": clicked_key
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/update_taskcard?access_token=' + access_token
    requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    return 0

def SendCardMessageToApp(UserId, Subject,  task_id):
    """
    发送任务卡片，UserId,Subject,Content,task_id均为string。
    task_id由zabbix的problem ID + @ + 时间戳制成。
    """
    GetResponse = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + CorpID + "&corpsecret=" + CorpSecret,
        proxies=proxy).json()
    access_token = (GetResponse['access_token'])

    rawdata = {
        "touser": UserId,
        "msgtype": "taskcard",
        "agentid": AgentID,
        "taskcard": {
            "title": Subject,
            "description": "↓",
            "task_id": task_id,
            "btn": [
                {
                    "key": "NextPage",
                    "name": "下一页",
                    "replace_name": "已请求下一页",
                }
            ]

        },
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata), proxies=proxy)
    print(PostContent.json())
    #print(rawdata)
    return 0