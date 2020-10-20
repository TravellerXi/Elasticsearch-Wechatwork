#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, request, abort
import logging
# 启用HTML模板模块jinja2。
from flask import render_template
# 多线程池
from concurrent.futures import ThreadPoolExecutor

from WeChatAPI.WeChatApiMethod import *
from Functions.CorpInfo import *
from Functions.VerifyUserInfo import *
from Functions.SearchMain import *

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=10)

@app.route('/', methods=['GET'])
def basic_get():
    """
    在GET里，我们处理了：1,企业回调认证。2，微信请求summary类型网页。3，微信请求Detail类型网页。
    :return: 返回HTML源码。
    """
    try:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        # logger.info('对方IP：'+IP)
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        # 上述几个变量的详细介绍在https://work.weixin.qq.com/api/doc/90000/90135/90930
        # 开始处理下一页请求
        Summary = str(request.args.get('summary'))
        Detail = str(request.args.get('detail'))
        try:
            (SearchContent, ResultSize, Page, UserID) = Summary.split(',')
            logger.info('该请求为微信请求summary')
        except:
            logger.info('该请求非summary')
        try:
            (SearchContent, ResultSize, SearchResultID) = Detail.split(',')
            logger.info('该请求为微信请求detail')
        except:
            logger.info('该请求非detail')

        Code = request.args.get('code')
        if EnableOAUTH is True:
            if Code is None:
                abort(404)
        if Summary != 'None':
            # 因为之前把Summary强制转换成string了
            if EnableOAUTH is True:
                if VerifyUserInfo(Code) == -1:
                    abort(404)
                else:
                    executor.submit(HandleMutiplePageSearchOnElstaic(SearchContent, UserID, Page))
                    return render_template('RequestNextClose.html')
            else:
                executor.submit(HandleMutiplePageSearchOnElstaic(SearchContent, UserID, Page))
                return render_template('RequestNextClose.html')
        elif Detail != 'None':
            if EnableOAUTH is True:
                if VerifyUserInfo(Code) == -1:
                    abort(404)
                else:
                    if Detail == 'zabbixsample':
                        return render_template('SampleSingleHost.html')
                    (HtmlString, HostName) = HandSpecificHostDetailedInfo(SearchResultID)
                    return render_template('SingleHost.html', SingleHostTitle='主机' + HostName + ' 的信息',
                                           SingleHostBody=HtmlString)
            else:
                if Detail == 'zabbixsample':
                    return render_template('SampleSingleHost.html')
                (HtmlString, HostName) = HandSpecificHostDetailedInfo(SearchResultID)
                return render_template('SingleHost.html', SingleHostTitle='主机' + HostName + ' 的信息',
                                       SingleHostBody=HtmlString)

        callback = HandleCallback(msg_signature, timestamp, nonce, echostr)
        if callback == -1:
            logger.error('回调解析失败，尝试调用HandleCallback时返回-1，访问者IP：' + IP + ',攻击方尝试访问URL:' + AttackURL + ',Method:GET')
            abort(404)
        return (callback)
    except Exception as e:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        logger.warning('非企业微信合法请求↓，访问者IP：' + IP + ',攻击方尝试访问URL:' + AttackURL + ',Method:GET')
        logger.warning(e)
        abort(404)


@app.route('/', methods=['POST'])
def basic_post():
    try:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        ReqData = request.get_data().decode()
        ReceiveMsg = DecodeMessage(msg_signature, timestamp, nonce, ReqData)
        if ReceiveMsg == -1:
            logger.error('解析用户发送数据失败，尝试调用DecodeMessage时返回-1，访问者IP：' + IP + ',攻击方尝试访问URL:' + AttackURL + ',Method:POST')
            return ''
        logger.info('ReceiveMsg:' + ReceiveMsg)
        # 仅取前三个值
        (Content, FromUserName, MsgType) = ReceiveMsg.split(',')[0:3]
        if MsgType == 'text':
            # 处理纯文本事件
            # 使用线程池执行器 ThreadPoolExecutor来并发执行任务和return，否则企业微信可能接收多条回复。
            executor.submit(SearchContentOnElstaic(Content, FromUserName))
        return ('')
    except Exception as e:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        logger.warning('非企业微信合法请求↓，访问者IP：' + IP + ',攻击方尝试访问URL:' + AttackURL + ',Method:GET')
        logger.warning(e)
        abort(404)

if __name__ == '__main__':
    logger = logging.getLogger()
    # 日志等级
    if LogLevel == '0':
        logger.setLevel(logging.DEBUG)
    elif LogLevel == '1':
        logger.setLevel(logging.INFO)
    elif LogLevel == '2':
        logger.setLevel(logging.WARNING)
    elif LogLevel == '3':
        logger.setLevel(logging.ERROR)
    elif LogLevel == '4':
        logger.setLevel(logging.CRITICAL)
    else:
        # 如无任何定义，默认等级为INFO
        logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LogDir, encoding='utf-8')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    logger.addHandler(handler)
    app.run(host=Host, port=Port, debug=Debug,processes=Processes)
