#!/usr/bin/env python3
# coding:utf-8

'''
搜索主引擎，处理从ElaasticAPI和微信中获取的数据
'''
# TODO：限定size和from/使用ID来确认URL '_id': '10897' TODO处理完毕
# TODO 修改一条主机直接返回。

from Functions.SendMsg import *
from Functions.ElasticAPI import *
import re
from urllib import parse

def HandleUserSendTxt(text:str):
    """
    接收用户发送的文字后替换中文状态下的冒号
    """
    HandledText=re.sub(re.compile(r'：'),':',text,count=0)
    return HandledText

# 企业微信OAUTH的URL，详情见https://work.weixin.qq.com/api/doc/90000/90135/91335
FirstPartUrl='https://open.weixin.qq.com/connect/oauth2/authorize?appid='+CorpID+'&redirect_uri='
LastPartUrl='&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
if EnableOAUTH is False:
    FirstPartUrl=''
    LastPartUrl=''


def SearchContentOnElstaic(SearchContent:str,UserId:str):
    SearchContent=HandleUserSendTxt(SearchContent)
    (RawData,ResultSize)=MyElasticSearch(SearchContent,DefineSize=3,SearchIndex='zabbix-host-info',Begins=0)

    # 无满足搜索要求
    if ResultSize==0:
        SendTextToApp(UserId, '无满足搜索要求的主机')
        return -1

    # 当ResultSize>=1个时，需要分页展示，先提供MarkDown的Summary。
    if ResultSize>=1:
        #RawContents ='搜索结果较多，以下展示概述:\n'
        RawContents=[]
        count=1
        for SignleSearchData in RawData:
            SearchResultID = SignleSearchData['_id']
            # 对URL进行encode，否则中文存在url，会报错
            SearchContent = parse.quote(SearchContent)
            DetailUrl='https://search.mytlu.cn:443/?detail='+SearchContent+','+str(ResultSize)+','+str(SearchResultID)
            DetailUrl=FirstPartUrl+DetailUrl+LastPartUrl
            RawContent='>结果 '+str(count)+':\n'
            HostName=SignleSearchData['_source']['主机名称']
            FullInterfaceIP=SignleSearchData['_source']['接口地址']
            if HostName is None:
                HostName=' '
            InterfaceIP=' '
            if len(FullInterfaceIP)>0:
                InterfaceIP = ''
                for SingleInterfaceIP in FullInterfaceIP:
                    InterfaceIP=InterfaceIP+SingleInterfaceIP+','
            if HostName=='':
                HostName='空'
            RawContent=RawContent+'>主机名称：['+HostName+']('+DetailUrl+')'+'\n'+'>接口地址：<font color="info">'+InterfaceIP+'</font>\n\n'

            RawContents.append(RawContent)
            count=count+1
        RawContentString=''
        for RawContent in RawContents:
            RawContentString=RawContentString+RawContent

        # 对URL进行encode，否则中文存在url，会报错
        SearchContent = parse.quote(SearchContent)

        RawContentString='为你找到以下'+str(ResultSize)+'条搜索结果，以下展示概述，点击主机名可查看主机详细信息:\n'+RawContentString
        url = 'https://search.mytlu.cn:443/?summary=' + SearchContent +','+ str(ResultSize)+','+'1,' + UserId

        url = FirstPartUrl + url + LastPartUrl
        NextPage = '\n\n>[下一页](' + url + ')'
        SearchEnd = '\n\n搜索结果显示完毕'
        if ResultSize>3:
            RawContentString = RawContentString + NextPage
        else:
            RawContentString = RawContentString + SearchEnd
        SendMarkDownToApp(UserId, RawContentString)
        return 0
    return -1

def HandleMutiplePageSearchOnElstaic(SearchContent:str,ResultSize:str,UserId:str,Page:str):
    SearchContent = HandleUserSendTxt(SearchContent)
    (RawData, SearchSize) = MyElasticSearch(SearchContent, DefineSize=4, SearchIndex='zabbix-host-info',Begins=(int(Page)*3))
    # 当RawData大于1个时，需要分页展示，先提供MarkDown的Summary。
    if SearchSize >= 1:
        # RawContents ='搜索结果较多，以下展示概述:\n'
        RawContents = []
        count = (int(Page)*3)+1
        for SignleSearchData in RawData:
            SearchResultID= SignleSearchData['_id']
            # 对URL进行encode，否则中文存在url，会报错
            SearchContent = parse.quote(SearchContent)
            DetailUrl = 'https://search.mytlu.cn:443/?detail=' + SearchContent +','+ ResultSize+ ',' + str(SearchResultID)

            DetailUrl=FirstPartUrl+DetailUrl+LastPartUrl
            RawContent = '>结果 ' + str(count) + ':\n'
            HostName = SignleSearchData['_source']['主机名称']
            FullInterfaceIP = SignleSearchData['_source']['接口地址']
            if HostName is None:
                HostName = ' '
            InterfaceIP = ' '
            if len(FullInterfaceIP) > 0:
                InterfaceIP = ''
                for SingleInterfaceIP in FullInterfaceIP:
                    InterfaceIP = InterfaceIP + SingleInterfaceIP + ','
            if HostName=='':
                HostName='空'
            RawContent = RawContent + '>主机名称：[' + HostName + ']('+DetailUrl+')' + '\n' + '>接口地址：<font color="info">' + InterfaceIP + '</font>\n\n'

            # RawContents=RawContents+RawContent
            RawContents.append(RawContent)
            count = count + 1
        RawContentString = ''
        #用来标记是否还有下一页
        TagEnd = 0
        try:
            RawContentString = RawContentString + RawContents[0]
        except:
            TagEnd = 1
        try:
            RawContentString = RawContentString + RawContents[1]
        except:
            TagEnd = 1
        try:
            RawContentString = RawContentString + RawContents[2]
        except:
            TagEnd = 1
        try:
            RawContents[3]
        except:
            TagEnd = 1

        RawContentString = '为你找到'+str(SearchSize)+'条搜索结果，以下展示概述，点击主机名可查看主机详细信息:\n' + RawContentString
        if TagEnd == 1:
            SearchEnd = '\n\n搜索结果显示完毕'
            RawContentString = RawContentString + SearchEnd
            SendMarkDownToApp(UserId, RawContentString)
        else:
            # 对URL进行encode，否则中文存在url，会报错
            SearchContent = parse.quote(SearchContent)
            url = 'https://search.mytlu.cn:443/?summary=' + SearchContent +','+str(SearchSize)+ ',' + str(int(Page) + 1) + ',' + UserId

            url=FirstPartUrl+url+LastPartUrl
            NextPage = '\n\n>[下一页](' + url + ')'
            RawContentString = RawContentString + NextPage
            SendMarkDownToApp(UserId, RawContentString)
        return 0

def HandSpecificHostDetailedInfo(SearchResultID:str):
    SearchResultID=int(SearchResultID)
    (RawData, SearchSize) = MyElasticSearch('_id:'+str(SearchResultID),DefineSize=1,SearchIndex='zabbix-host-info',Begins=0)
    SpecificInfo=RawData[0]['_source']
    HtmlString = ''
    HostName=''
    for SigleName in SpecificInfo:
        HtmlString = HtmlString + SigleName + ': '
        if ((SpecificInfo[SigleName])) == None:
            HtmlString = HtmlString + '无<br>'
        elif SigleName == '接口地址' or SigleName == '主机组':
            SingleContents = ''
            for SingleContent in (SpecificInfo[SigleName]):
                SingleContents = SingleContents + ' ' + SingleContent + ','
            HtmlString = HtmlString + SingleContents + '<br>'

        else:
            HtmlString = HtmlString + str((SpecificInfo[SigleName])) + '<br>'
        if SigleName=='主机名称':
            HostName=SpecificInfo[SigleName]
    return (HtmlString,HostName)
