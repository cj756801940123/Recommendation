#!/usr/bin/python
# -*- coding:utf-8 -*-
from snownlp import SnowNLP
from snownlp import sentiment
from Recommedation.analyse import similarity_util
from Recommedation.analyse import thread_queue
from Recommedation.common import database_util
import re
import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

def get_unreal_comment(table):
    sql = 'select sku from '+table+' where update_unreal_time is null'
    result = database_util.search_sql(sql,None)
    sku_list = []
    if result[0]!=-1:
        times = list(result[1])
        for i in times:
            sku_list.append(i[0])
    thread_queue.fill_queue(sku_list)
    thread_queue.use_threading(['get_unreal_comment',table])

#把useful文件里面的刷单评价删掉
def del_unreal_comment(table):
    sql = 'select sku from ' + table + ' where update_unreal_time is not null'
    result = database_util.search_sql(sql, None)
    sku_list = []
    if result[0] != -1:
        times = list(result[1])
        for i in times:
            sku_list.append(i[0])
    thread_queue.fill_queue(sku_list)
    thread_queue.use_threading(['del_unreal_comment', table])

#可以分析了
def get_sentiment_score(table):
    sql = 'select sku from ' + table + ' where update_unreal_time is not null'
    result = database_util.search_sql(sql, None)
    sku_list = []
    if result[0] != -1:
        times = list(result[1])
        for i in times:
            sku_list.append(i[0])
    thread_queue.fill_queue(sku_list)
    thread_queue.use_threading(['get_sentiment_score', table])


if __name__ == '__main__':
    table = 'cellphone'
    # get_unreal_comment(table)
    del_unreal_comment(table)
    # get_sentiment_score(table)

