#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

from Recommedation.common import database_util
from Recommedation.update import thread_queue

FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')


def update_price(table):
    sql = 'SELECT sku,max_price,min_price,avg_price,price_times  FROM '+table+ ' where TO_DAYS(NOW()) - TO_DAYS(update_price_time) >=1';
    result = database_util.search_sql(sql, None)
    prices = []
    if result[0]!=-1:
        times = list(result[1])
        for i in times:
            price = {}
            price['sku'] = i[0]
            price['max_price'] = float(i[1])
            price['min_price'] = float(i[2])
            price['avg_price'] = float(i[3])
            price['price_times'] = int(i[4])
            prices.append(price)
    thread_queue.fill_queue(prices)
    thread_queue.use_threading(['update_price',table])

def update_shop_info(table):
    sql = 'SELECT shop_id FROM '+table+ ' where TO_DAYS(NOW()) - TO_DAYS(update_shop_time) >=1';
    result = database_util.search_sql(sql, None)
    shop_id = []
    if result[0]!=-1:
        id = list(result[1])
        for i in id:
            if i[0] is not None:
                # print(i[0])
                shop_id.append(i[0])
            else:
                print("shop_id is null")
    thread_queue.fill_queue(shop_id)
    thread_queue.use_threading(['update_shop_info',table])

    sql = 'select brand,follow from '+table+' group by brand order by follow'
    result = database_util.search_sql(sql,None)
    if result[0]!=-1:
        result = list(result[1])
    for i in result:
        sql = 'update '+table+' set brand_hot=%s where brand=%s'
        data = [i[1],i[0]]
        database_util.update_sql(sql,data)

def get_shop_id(table):
    sql = 'SELECT sku FROM '+table+ ' where shop_id is null';
    result = database_util.search_sql(sql, None)
    sku = []
    if result[0]!=-1:
        id = list(result[1])
        for i in id:
            if i[0] is not None:
                sku.append(i[0])
            else:
                print("sku is null")
    thread_queue.fill_queue(sku)
    thread_queue.use_threading(['get_shop_id',table])

def get_comment(table):
    sql = 'SELECT sku FROM '+table+ ' where follow>=10000 and comment>=3000 and comment<5000';
    # sql = 'SELECT sku FROM '+table+ ' where follow>=100000 and TO_DAYS(NOW()) - TO_DAYS(update_comment_time) >=5';
    # sql = 'SELECT sku FROM '+table+ ' where follow>=100000';
    result = database_util.search_sql(sql, None)
    sku = []
    if result[0]!=-1:
        id = list(result[1])
        for i in id:
            if i[0] is not None:
                # print(i[0])
                sku.append(i[0])
            else:
                print("sku is null")
    thread_queue.fill_queue(sku)
    #第三个参数是要获取多少页的评论数据
    thread_queue.use_threading(['get_comment',table,100])

def update_score(table):
    sql = 'select * from weight'
    result = database_util.search_sql(sql, None)
    para = {}
    if result[0] != -1:
        result = list(result[1])
        for i in result:
            sum = i[1] + i[2] + i[3] + i[4] + i[5]
            para['w_rate'] = float(i[1]) / sum
            para['w_follow'] = float(i[2]) / sum
            para['w_comment'] = float(i[3]) / sum
            para['w_sentiment'] = float(i[4]) / sum
            para['w_brand'] = float(i[5]) / sum

    sql = 'select follow from ' + table + ' order by follow desc limit 1'
    result = database_util.search_sql(sql, None)
    if result[0] != -1:
        result = list(result[1])
        para['w_follow'] = para['w_follow']*100.0/result[0][0]
        para['w_brand'] = para['w_brand'] * 100.0 / result[0][0]

    sql = 'select comment from ' + table + ' order by comment desc limit 1'
    result = database_util.search_sql(sql, None)
    if result[0] != -1:
        result = list(result[1])
        para['w_comment'] = para['w_comment']*100.0/result[0][0]

    sql = 'select sku from ' + table
    result = database_util.search_sql(sql, None)
    if result[0] != -1:
        result = list(result[1])
        sku_list = []
        for i in result:
            sku_list.append(i[0])
        thread_queue.fill_queue(sku_list)
        thread_queue.use_threading(['update_score',table,para])


if __name__ == '__main__':
    table = 'cellphone'
    update_price(table)
    # get_shop_id(table)
    # update_shop_info(table)
    # update_score(table)