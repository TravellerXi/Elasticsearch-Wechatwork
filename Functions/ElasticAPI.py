#!/usr/bin/env python3
# coding:utf-8
from elasticsearch import Elasticsearch
from Functions.CorpInfo import *
es = Elasticsearch([{'host':ELHost,'port':ELPort}],timeout=ELTimeout)

def MyElasticSearch(SearchContent:str,DefineSize:int,SearchIndex:str,Begins:int):
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


