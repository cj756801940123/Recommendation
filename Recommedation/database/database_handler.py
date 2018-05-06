#!/usr/bin/python
# -*- coding:utf-8 -*-
import pymysql
from Recommedation.spider import phone_item
import datetime
import os
import re

def search_item(sku):
    try:
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,
                             charset="utf8")
        cur = db.cursor()  # 获取操作游标
        sql = "select * from cellphones where number= %s"
        data = (sku)
        cur.execute(sql,data)  # 执行sql语句
        results = cur.fetchall()  # 获取查询的所有记录
        if len(results) > 0:
            print("item is already in database")
            return 1
    except Exception as err:
        print("fail to search item in database,err:"+str(err))
    finally:
        db.close()  # 关闭连接
    return -1

def search_sku(file_path):
    try:
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,
                             charset="utf8")
        cur = db.cursor()  # 获取操作游标
        sql = "select distinct number from cellphones "
        cur.execute(sql)  # 执行sql语句
        results = list(cur.fetchall())  # 获取查询的所有记录
        print(results)
        file = open(file_path + 'procedure_files/unsolved_skus.txt', "a", encoding='utf-8')
        for i in results:
            file.write(i[0]+'\n')
    except Exception as err:
        print("fail to search item in database,err:"+str(err))
    finally:
        file.close()
        db.close()  # 关闭连接

def save_item(item,table_name):
    try:
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,
                             charset="utf8")
        cursor = db.cursor()  # 获取操作游标
        cursor.execute(
            "INSERT INTO %s(address,description,price,img_address,brand,name,number,operating_system,ram,rom ,get_time)"
            "VALUES ('%s','%s','%f','%s','%s','%s','%s','%s','%s','%s','%s')"
            %(table_name,item.address,item.description,item.price,item.img_address,item.brand,
            item.name,item.number,item.operating_system,item.ram,item.rom,item.get_time)
        )
        db.commit()
    except Exception as err:
        print('fail to save item to database,err:'+str(err))
        return -1
    finally:
        db.close()  # 关闭连接

if __name__ == '__main__':
    # item = phone_item.getItem()
    # item.price = 100.1
    # item.get_time = datetime.datetime.now()
    # save_item(item, "test")
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_handler.py")))) + '/data/').replace('\\',                                                                                '/')
    # search_sku(file_path)
    # update_rate(file_path)
    # search_item("cellphones", "22925635489")
