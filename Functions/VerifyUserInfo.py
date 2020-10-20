#!/usr/bin/env python3
# coding:utf-8
"""
企业微信OAUTH认证的接口，详情见https://work.weixin.qq.com/api/doc/90000/90135/91335
"""
import requests
from Functions.CorpInfo import *

def VerifyUserInfo(Code):
    """
    :param Code: 企业微信返回的Code
    :return: 是否认证成功，0成功，其他不成功。
    """
    GetResponse = requests.request("get",
                                   "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + CorpID + "&corpsecret=" + CorpSecret,
                                   proxies=proxy).json()
    access_token = (GetResponse['access_token'])
    GetResponse = requests.request("get",
                                   "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token="+access_token+"&code=" + Code,
                                   proxies=proxy).json()
    if not (GetResponse['errcode'] == 0):
        return -1
    else:
        return 0