#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, request, abort, send_file
from Functions.SendMsg import *
import logging
# 启用HTML模板模块jinja2。
from flask import render_template

from WeChatAPI.WeChatApiMethod import *
from Functions.CorpInfo import *
from Functions.Search import *
#from Functions.WebSource import  *
from Functions.VerifyUserInfo import *
app = Flask(__name__)

@app.route('/', methods=['GET'])
def basic_get():
    IP = request.headers.get('X-Forwarded-For')
    AttackURL = request.url
    # logger.info('对方IP：'+IP)
    msg_signature = request.args.get('msg_signature')
    timestamp = request.args.get(('timestamp'))
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')

    # 开始处理下一页请求
    Summary= str( request.args.get('summary'))
    Detail = str( request.args.get('detail'))
    try:
        (SearchContent, ResultSize,Page, UserID )=Summary.split(',')
    except:
        logger.info('该请求非summary')
    try:
        (SearchContent, ResultSize, SearchResultID) = Detail.split(',')
    except:
        logger.info('该请求非detail')

    Code=request.args.get('code')
    if EnableOAUTH is True:
        if Code is None:
            abort(404)
    if Summary !='None':#因为之前把Summary强制转换成string了
        if EnableOAUTH is True:
            if VerifyUserInfo(Code)==-1:
                abort(404)
            else:
                HandleMutiplePageSearchOnElstaic(SearchContent, str(3), UserID, Page)
                #return OneSecondsToClose
                return render_template('RequestNextClose.html')
        else:
            HandleMutiplePageSearchOnElstaic(SearchContent, str(3), UserID, Page)
            #return OneSecondsToClose
            return render_template('RequestNextClose.html')
    elif Detail !='None':
        if EnableOAUTH is True:
            if VerifyUserInfo(Code) == -1:
                abort(404)
            else:
                (HtmlString,HostName)=HandSpecificHostDetailedInfo(SearchResultID)
                #return HandSpecificHostDetailedInfo(SearchResultID)
                return render_template('SingleHost.html',SingleHostTitle='主机'+HostName+' 的信息',SingleHostBody=HtmlString)
        else:
            (HtmlString, HostName) = HandSpecificHostDetailedInfo(SearchResultID)
            #return HandSpecificHostDetailedInfo(SearchResultID)
            return render_template('SingleHost.html', SingleHostTitle='主机' + HostName + ' 的信息', SingleHostBody=HtmlString)

    # 上述几个变量的详细介绍在https://work.weixin.qq.com/api/doc/90000/90135/90930
    callback = HandleCallback(msg_signature, timestamp, nonce, echostr)
    if callback == -1:
        logger.error('回调解析失败，尝试调用HandleCallback时返回-1，访问者IP：' + IP + ',攻击方尝试访问URL:' + AttackURL + ',Method:GET')
        abort(404)
    return (callback)

@app.route('/', methods=['POST'])
def basic_post():
    msg_signature = request.args.get('msg_signature')
    timestamp = request.args.get(('timestamp'))
    nonce = request.args.get('nonce')
    ReqData = request.get_data().decode()
    ReceiveMsg = DecodeMessage(msg_signature, timestamp, nonce, ReqData)
    logger.info('ReceiveMsg:' + ReceiveMsg)
    Content = ReceiveMsg[:-1].split(',')[0]
    FromUserName = ReceiveMsg[:-1].split(',')[1]  #即USERID，企业微信的ID
    MsgType = ReceiveMsg[:-1].split(',')[2]
    ##我们从上面就获取了FromUserName和Content。下面我们要回复消息给微信
    if MsgType == 'text':
        # 处理纯文本事件
        SearchContentOnElstaic(Content,FromUserName)
    return ('')

if __name__ == '__main__':
    logger = logging.getLogger()
    app.run(host='localhost', port=825, debug=False,threaded=True)
