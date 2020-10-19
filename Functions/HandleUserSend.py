#!/usr/bin/env python3
# coding:utf-8
import re
from Functions.CorpInfo import *

def HandleUserSendTxt(text:str):
    """
    接收用户发送的文字后进行合适的处理
    """
    HandledText=re.sub(re.compile(r'：'),':',text,count=0)
    return HandledText