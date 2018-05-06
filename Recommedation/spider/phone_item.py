#!/usr/bin/python
# -*- coding:utf-8 -*-
class PhoneItem(object):
    def __init__(self):
        self.address = ''               #商品链接网址
        self.description = ''           #商品全称，比如"OPPO R11s 全面屏双摄拍照手机 4GB+64GB 黑色 全网通 移动联通电信4G 双卡双待手机 "
        self.price = 1999               #decimal(10,2) NULL
        self.img_address = ''           #商品图片的链接地址
        self.brand = ''                 #品牌，比如oppo
        self.name = ''                  #商品名字，比如oppor11
        self.number = ''                #varchar(30) NULL COMMENT商品编号，比如1458853
        self.operating_system = ''        # 操作系统,例如安卓（Android）
        self.ram =''                    #运行内存
        self.rom = ''                   #机身内存
        self.get_time = ''

        self.screen_score = 70          #屏幕
        self.server = 85                #服务
        self.touch = 83                 #手感
        self.system = 79                #系统
        self.cost_effective = 80        #性价比
        self.battery = 75               #电池
        self.appearance = 84            #外观
        self.quality = 75               #质量
        self.genuine = 82               #正品
        self.camera = 76                #摄像头
        self.game = 70                  #游戏
        self.earphone = 60              #耳机
        self.storage = 72               #内存

def getItem():
    item = PhoneItem()
    return item
