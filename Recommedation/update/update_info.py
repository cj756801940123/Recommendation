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


def del_items(table):
    sql = 'delete from '+table+' where shop_name is null;'
    database_util.update_sql(sql,None)

def del_file(table):
    path_list = [DATA_PATH+table+'/item_comments/',DATA_PATH+table+'/useful_comments/']
    for file_path in path_list:
        for sku_name in os.listdir(file_path):
            sku = sku_name[0:sku_name.find('.')]
            sql = 'select shop_name from '+table+' where sku=%s'
            result = database_util.search_sql(sql,sku)
            if result[0]!=-1:
                if len(result[1])==0:
                    print('deleted sku:%s'%(sku))

def update_img(table):
    sql = 'select img from '+table
    database_util.search_sql(sql,None)


if __name__ == '__main__':
    table = 'cellphone'
    del_file(table)
    # del_items(table)