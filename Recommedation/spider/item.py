#!/usr/bin/python
# -*- coding:utf-8 -*-
class Item(object):
    def __init__(self):
        self.url = ''                   #商品链接网址
        self.description = ''           #商品全称，比如"OPPO R11s 全面屏双摄拍照手机 4GB+64GB 黑色 全网通 移动联通电信4G 双卡双待手机 "
        self.price = 1999               #decimal(10,2) NULL
        self.img = ''                   #商品图片的链接地址
        self.brand = ''                 #品牌，比如oppo
        self.name = ''                  #商品名字，比如oppor11
        self.number = ''                #varchar(30) NULL COMMENT商品编号，比如1458853
        self.get_time = ''


def getItem():
    item = Item()
    return item
