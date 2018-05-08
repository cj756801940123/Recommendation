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

def update_img(table):
    sql = 'select img from '+table
    database_util.search_sql(sql,None)


if __name__ == '__main__':
    table = 'cellphone'
    # update_price(table)
    # get_shop_id(table)
    # update_shop_info(table)
    del_items(table)