#!/usr/bin/env python3
# coding:utf-8

""" 
整合CorpInfo.ini里的配置信息，传递到所有程序中
"""

import os
import configparser

CurrentDir=os.getcwd()
AbsolutePath = CurrentDir+'/Configure.ini'
config = configparser.ConfigParser()
config.read(AbsolutePath, encoding='utf-8')


# begin 企业微信相关信息
Token = config.get('CorpWechat', 'Token')
EncodingAESKey = config.get('CorpWechat', 'EncodingAESKey')
CorpID = config.get('CorpWechat', 'CorpID')
CorpSecret = config.get('CorpWechat', 'CorpSecret')
AgentID = config.get('CorpWechat', 'AgentID')
if config.get('CorpWechat', 'EnableOAUTH')=='1':
    EnableOAUTH =True
else:
    EnableOAUTH = False
# end 企业微信相关信息

# begin 部署环境网络代理信息
proxy = {'http': config.get('Network', 'Proxy'), 'https': config.get('Network', 'Proxy')}
#end 部署环境网络代理信息

# begin Web服务器的配置信息
Host = config.get('WebSetting', 'Host')
Port = int(config.get('WebSetting', 'Port'))

# LogDir,未定义，默认/opt/Zabbix-WechatWork/main.log
try:
    LogDir = config.get('WebSetting', 'LogDir')
except:
    LogDir = '/opt/Zabbix-WechatWork/main.log'

# LogLevel,未定义，默认'1'
try:
    LogLevel = str(config.get('WebSetting', 'LogLevel'))
except:
    LogLevel = '1'
if config.get('WebSetting', 'Debug')=='1':
    Debug=True
elif config.get('WebSetting', 'Debug')=='0':
    Debug=False
# Debug，未定义，默认False
else:
    Debug=False
if config.get('WebSetting', 'Processes')=='1':
    Processes=True
elif config.get('WebSetting', 'Processes')=='0':
    Processes=False
# Processes，未定义，默认True
else:
    Processes=True
ExternalURL=config.get('WebSetting', 'ExternalURL')
# end Web服务器的配置信息

# begin ElasticSearchServer
ELHost=config.get('ElasticSearchServer', 'ELHost')
ELPort=config.get('ElasticSearchServer', 'ELPort')
ELTimeout=int(config.get('ElasticSearchServer', 'ELTimeout'))
# end ElasticSearchServer

# begin OAUTH URL
# 企业微信OAUTH的URL，详情见https://work.weixin.qq.com/api/doc/90000/90135/91335
FirstPartUrl = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + CorpID + '&redirect_uri='
LastPartUrl = '&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
if EnableOAUTH is False:
    FirstPartUrl = ''
    LastPartUrl = ''
# end OAUTH URL