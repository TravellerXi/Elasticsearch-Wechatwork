#!/usr/bin/env python3
# coding:utf-8

"""
搜索主引擎，处理从ElasticAPI和微信中获取的数据
主要函数在SearchFunction.py
"""

from Functions.SearchFunction import *

def SearchContentOnElstaic(SearchContent:str,UserId:str):
    """
    使用搜索内容和用户ID返回企业微信搜索第一页
    :param SearchContent: 搜索内容
    :param UserId: 用户企业微信ID
    :return: 企业微信搜索第一页
    """
    # 开始 帮助信息
    if SearchContent=='帮助':
        # 开始 拼凑帮助信息
        HelpContent='>帮助信息\n\n>  <font color="info">发送跟主机相关的信息（主机名、IP等）即可模糊查找主机</font>'
        HelpContent=HelpContent+'\n\n>  <font color="info">支持lucene语法。可通过类似“主机名称:k8s-node2”进行条件查找</font>'
        HelpContent = HelpContent + '\n\n> <font color="info">发送“帮助-条件查找-条件”获取主机信息的细节。可用于条件查找</font>\n'
        # 结束 拼凑帮助信息
        SendMarkDownToApp(UserId, HelpContent)
        return 0
    if SearchContent=='帮助-条件查找-条件':
        # 开始拼凑帮助信息
        HelpContent = '>帮助-条件查找-条件\n\n'
        HelpContent = HelpContent + '\n\n>  <font color="info">可用于条件查找的条件有“主机名称，主机别名，接口地址，主机组”等</font>'
        URL=FirstPartUrl+ExternalURL+'?detail=zabbixsample'+LastPartUrl
        HelpContent=HelpContent+'\n\n> 更多条件，[点此查看模板主机]('+URL+')\n'
        # 结束拼凑帮助信息
        SendMarkDownToApp(UserId, HelpContent)
        return 0
    # 结束 帮助信息

    # 使用正则表达式将用户发送的中文冒号转换成英文冒号
    SearchContent = HandleUserSendTxt(SearchContent)
    # 对于DefineSize=3，默认先获取搜索结果的三个值。方便直接返回。
    (RawData, ResultSize) = MyElasticSearch(SearchContent, DefineSize=3, SearchIndex='zabbix-host-info', Begins=0)


    # 无满足搜索要求
    if ResultSize==0:
        SendTextToApp(UserId, '无满足搜索要求的主机，发送”帮助“获取帮助信息')
        return -1

    # 当ResultSize>=1个时，需要分页展示，先提供MarkDown的Summary。
    if ResultSize>=1:
        # 这是发起搜索，所以第一页为Page=0
        HandleSearchRawContent(SearchContent, RawData, ResultSize, Page=0, UserId=UserId)
        return 0
    return -1

def HandleMutiplePageSearchOnElstaic(SearchContent:str,UserId:str,Page:str):
    """
    使用搜索内容，搜索有多少结果，用户ID，PAGEID来返回下一页的summary
    :param SearchContent: 搜索内容
    :param UserId: 用户ID
    :param Page: 是从第几页请求的
    :return: 返回下一页的Sumamry内容。
    """

    # 使用正则表达式将用户发送的中文冒号转换成英文冒号
    SearchContent = HandleUserSendTxt(SearchContent)
    (RawData, SearchSize) = MyElasticSearch(SearchContent, DefineSize=3, SearchIndex='zabbix-host-info',Begins=(int(Page)*3))

    # 当RawData大于1个时，需要分页展示，提供MarkDown的Summary。
    if SearchSize >= 1:
        HandleSearchRawContent(SearchContent, RawData, SearchSize, Page=Page, UserId=UserId)
    # 此函数被调用时，应该只满足SearchSize >= 1,因此直接结束。
    return 0



def HandSpecificHostDetailedInfo(SearchResultID:str):
    """
    接收返回的ID，精确返回ID的HTML结果。
    :param SearchResultID: string type。Search result里的每个结果的ID
    :return: ID的搜索结果
    """

    # 使用正则表达式将用户发送的中文冒号转换成英文冒号
    SearchResultID=int(SearchResultID)
    (RawData, SearchSize) = MyElasticSearch('_id:'+str(SearchResultID),DefineSize=1,SearchIndex='zabbix-host-info',Begins=0)

    # 进一步提取单个主机的信息，拼凑成HTML，填充到templates/SingleHost.html里的SingleHostBody部分。
    # 开始 拼凑HTML
    SpecificInfo=RawData[0]['_source']
    HtmlString = ''
    HostName=''
    for SingleName in SpecificInfo:
        HtmlString = HtmlString + SingleName + ': '
        if (SpecificInfo[SingleName]) == None:
            HtmlString = HtmlString + '无<br>'
        elif SingleName == '接口地址' or SingleName == '主机组':
            SingleContents = ''
            for SingleContent in (SpecificInfo[SingleName]):
                SingleContents = SingleContents + ' ' + SingleContent + ','
            HtmlString = HtmlString + SingleContents + '<br>'

        else:
            HtmlString = HtmlString + str((SpecificInfo[SingleName])) + '<br>'
        if SingleName=='主机名称':
            HostName=SpecificInfo[SingleName]
    # 结束 拼凑HTML
    return (HtmlString,HostName)
