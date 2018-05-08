#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from Recommedation.common import file_util
from Recommedation.common import item
from Recommedation.database import database_util
from Recommedation.spider import jd_spider
from Recommedation.update import thread_queue
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

def update_price(table):
    sql = 'SELECT sku,max_price,min_price,avg_price,price_times  FROM '+table+ ' where TO_DAYS(NOW()) - TO_DAYS(update_price_time) >=1';
    result = database_util.search_sql(sql,None)
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
    result = database_util.search_sql(sql,None)
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

def get_shop_id(table):
    sql = 'SELECT sku FROM '+table+ ' where shop_id is null';
    result = database_util.search_sql(sql,None)
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
    sql = 'SELECT sku FROM '+table+ ' where follow_count>=10000 and comment_count>=3000 and comment_count<5000';
    # sql = 'SELECT sku FROM '+table+ ' where follow_count>=100000 and TO_DAYS(NOW()) - TO_DAYS(update_comment_time) >=5';
    # sql = 'SELECT sku FROM '+table+ ' where follow_count>=100000';
    result = database_util.search_sql(sql,None)
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


if __name__ == '__main__':
    table = 'cellphone'
    # update_price(table)
    # get_shop_id(table)
    # update_shop_info(table)
    get_comment(table)
# https://img12.360buyimg.com/n7/jfs/t16648/185/641797811/166080/e96a680b/5a9d248cN071f4959.jpg
# https://img12.360buyimg.com/n7/jfs/t6010/111/3843138696/73795/bf58700d/5959ab7fN154e56b4.jpg
# https://img12.360buyimg.com/n5/s54x54_jfs/t6010/111/3843138696/73795/bf58700d/5959ab7fN154e56b4.jpg
# https://img14.360buyimg.com/n5/s54x54_jfs/t12757/25/2225525837/224733/6d43c72f/5a372c9bNe02f170c.jpg
# https://img11.360buyimg.com/n5/s54x54_jfs/t9247/117/1333322015/135772/bb51bc5/59bf69dbN6fa46cea.jpg

# https://img12.360buyimg.com/n7/jfs/t16327/64/2674134727/179245/ec830987/5ab9e7d7N66383b39.jpg