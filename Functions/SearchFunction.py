#!/usr/bin/env python3
# coding:utf-8
"""
SearchMain.py 的函数库
"""

import re
from Functions.CorpInfo import *
from urllib import parse
from Functions.SendMsg import *
from Functions.ElasticAPI import *

def HandleUserSendTxt(text:str):
    """
    接收用户发送的文字后，使用正则表达式替换中文状态下的冒号
    """
    # count=0 ，替换所有匹配项。
    HandledText=re.sub(re.compile(r'：'),':',text,count=0)
    return HandledText

def HandleSearchRawContent(SearchContent:str,RawData:list,SearchSize:str,Page,UserId:str):
    """
    在SearchMain.SearchContentOnElstaic中，默认 ResultSize>=1才可使用本函数。
    处理Search内容成Markdown语言，发送给用户。
    :param SearchContent: 搜索内容
    :param RawData:通过ElasticAPI.MyElasticSearch后返回的RawData
    :param SearchSize:对于搜索内容返回的搜索结果，多少个搜索结果
    :param Page:页码，默认从0开始，但是传递出来的第一个是1.
    :param UserId:用户企业微信ID
    :return:0：success，其他：错误。
    """
    SearchSize=str(SearchSize)
    Page=str(Page)
    RawContents = ''
    count = (int(Page) * 3) + 1
    for SignleSearchData in RawData:
        SearchResultID = SignleSearchData['_id']
        # 对URL中除协议、主机名、端口号之外，都进行encode，否则中文存在url，会报错。参考https://www.cnblogs.com/hushuai-ios/p/5500162.html
        PartURL = '?detail=' + SearchContent + ',' + SearchSize + ',' + str(SearchResultID)
        # 确认是否启用微信OAUTH
        if EnableOAUTH is True:
            PartURL = parse.quote(PartURL)
        DetailUrl = ExternalURL + PartURL
        DetailUrl = FirstPartUrl + DetailUrl + LastPartUrl

    # 开始 拼凑Markdown语言
        RawContent = '>结果 ' + str(count) + ':\n'
        HostName = SignleSearchData['_source']['主机名称']
        FullInterfaceIP = SignleSearchData['_source']['接口地址']
        if (HostName is None) or (HostName == ''):
            HostName = '空'
        InterfaceIP = ' '
        if len(FullInterfaceIP) > 0:
            InterfaceIP = ''
            for SingleInterfaceIP in FullInterfaceIP:
                InterfaceIP = InterfaceIP + SingleInterfaceIP + ','
        RawContent = RawContent + '>主机名称：[' + HostName + '](' + DetailUrl + ')' + '\n' + '>接口地址：<font color="info">' + InterfaceIP + '</font>\n\n'

        RawContents=RawContents+RawContent
        count = count + 1

    # TagEnd 用来标记是否还有下一页,1无，0有。
    if int(SearchSize) >(int(Page) * 3 + 3):
        TagEnd = 0
    else:
        TagEnd = 1

    RawContents = '关于"'+SearchContent+'"\n\n>为你找到' + str(SearchSize) + '条搜索结果，以下展示概述，点击主机名可查看主机详细信息:\n\n' + RawContents
    if TagEnd == 1:
        SearchEnd = '\n\n搜索结果显示完毕'
        RawContents = RawContents + SearchEnd
        SendMarkDownToApp(UserId, RawContents)
    else:
        # 对URL中除协议、主机名、端口号之外，都进行encode，否则中文存在url，会报错。参考https://www.cnblogs.com/hushuai-ios/p/5500162.html
        PartURL = '?summary=' + SearchContent + ',' + str(SearchSize) + ',' + str(int(Page) + 1) + ',' + UserId
        if EnableOAUTH is True:
            PartURL = parse.quote(PartURL)
        url = ExternalURL + PartURL
        url = FirstPartUrl + url + LastPartUrl
        NextPage = '\n\n>[下一页](' + url + ')'
        RawContents = RawContents + NextPage
        SendMarkDownToApp(UserId, RawContents)
    # 结束 拼凑Markdown语言
    return 0

