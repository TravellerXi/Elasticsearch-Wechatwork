#!/usr/bin/env python3
# coding:utf-8
from elasticsearch import Elasticsearch
from Functions.CorpInfo import *

def MyElasticSearch(SearchContent:str,DefineSize:int,SearchIndex:str,Begins:int):
    """
    ElasticSearch API
    :param SearchContent:
    :param DefineSize:
    :param SearchIndex:
    :param Begins:
    :return: 返回Search结果的原始数据及一共有几个结果。RawData,ResultSize
    """
    es = Elasticsearch([{'host': ELHost, 'port': ELPort}], timeout=ELTimeout)
    DefineSize=int(DefineSize)
    Begins=int(Begins)
    # from 默认从0开始
    RawData = (es.search(index=SearchIndex, q=SearchContent, size=DefineSize,from_=Begins))
    ResultSize=RawData['hits']['total']['value']
    try :
        RawData=RawData['hits']['hits']
    except:
        return -1
    return (RawData,ResultSize)


