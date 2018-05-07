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

#获取待更新的url放进文件里
def get_unsloved_file(table,type):
    global UNSOLVED_FILE
    global SOLVED_FILE
    global ERR_FILE
    UNSOLVED_FILE = FILE_PATH+'update_files/unsolved_'+table+'_'+type+'s.txt'
    SOLVED_FILE = FILE_PATH+'update_files/solved_'+table+'_'+type+'s.txt'
    ERR_FILE = FILE_PATH+'update_files/err_'+table+'_'+type+'s.txt'

    sql = 'select distinct '+type+' from '+table;
    sql_results = database_util.search_sql(sql,None)
    if sql_results[0] == -1:
        return
    temp = list(sql_results[1])
    out_file = open(UNSOLVED_FILE, "w", encoding='utf-8')
    for j in temp:
        url =  list(j)[0]
        out_file.write(url + '\n')
    out_file.close()

    if os.path.exists(SOLVED_FILE):
        os.remove(SOLVED_FILE)

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

def update_follow_count(table):
    sql = 'SELECT shop_id FROM '+table+ ' where TO_DAYS(NOW()) - TO_DAYS(update_shop_time) >=1';
    result = database_util.search_sql(sql,None)
    shop_id = []
    if result[0]!=-1:
        id = list(result[1])
        for i in id:
            if i[0] is not None:
                print(i[0])
                shop_id.append(i[0])
            else:
                print("shop_id is null")
    thread_queue.fill_queue(shop_id)
    thread_queue.use_threading(['update_follow_count',table])

def get_shop_info(table):
    pass

if __name__ == '__main__':
    table = 'cellphone'
    # update_price(table)
    update_follow_count(table)



