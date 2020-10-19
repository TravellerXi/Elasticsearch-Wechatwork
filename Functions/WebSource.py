#!/usr/bin/env python3
# coding:utf-8
# TODO 学习下Flask模板

OneSecondsToClose='''
<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>下一页数据请求成功</title>
<SCRIPT LANGUAGE="JavaScript">
<!--
  setTimeout("window.opener=null;window.close()",1000);
-->
</SCRIPT>
</head>
<body>
下一页数据请求成功，页面将于1秒内关闭
</body>
</html>

'''
SpecificHostSourceBegin='''
<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>详情</title>
<body>
'''
SpecificHostSourceBegin='''
</body>
</html>
'''