#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

from Recommedation.common import database_util

FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')


def del_items(table):
    sql = 'delete from '+table+' where shop_name is null;'
    database_util.update_sql(sql, None)

def del_file(table):
    path_list = [DATA_PATH+table+'/item_comments/',DATA_PATH+table+'/useful_comments/']
    for file_path in path_list:
        for sku_name in os.listdir(file_path):
            sku = sku_name[0:sku_name.find('.')]
            sql = 'select shop_name from '+table+' where sku=%s'
            result = database_util.search_sql(sql, sku)
            if result[0]!=-1:
                if len(result[1])==0:
                    print('deleted sku:%s'%(sku))

def update_img(table):
    sql = 'select img from '+table
    database_util.search_sql(sql, None)

def update_score(user,table):
    sql ='select rate,follow_count,comment_count,sentiment,brand_hot from weight weher user=%s  and kind=%s'
    data =[user,table]
    result = database_util

def update_img(table):
    sql = 'select img,sku from '+table
    result = database_util.search_sql(sql, None)
    if result[0]!=-1:
        imgs = list(result[1])
        for i in imgs:
            img = i[0]
            sku = i[1]
            print(img)
            new_img = img.replace('n5/s54x54_jfs','n7/jfs')
            print(new_img+'\n')

            sql = 'update '+table+' set img=%s where sku=%s'
            data = [new_img,sku]
            database_util.update_sql(sql,data)

# https://img11.360buyimg.com/n5/s54x54_jfs/t5773/143/1465870132/216483/4bbce005/592692d8Nbcc8f248.jpg
# https://img10.360buyimg.com/n7/jfs/t18772/89/1863054684/170815/d28ecae1/5adca3deN76bb61cb.jpg

if __name__ == '__main__':
    table = 'cellphone'
    update_img(table)