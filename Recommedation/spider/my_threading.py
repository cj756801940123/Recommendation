#!/usr/bin/python
# -*- coding:utf-8 -*-
# import urllib
import urllib
import json
import time
import datetime
import threading
import queue
from Recommedation.spider import jd_spider
import sys
import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

UNSOLVED_FILE = ''
SOLVED_FILE = ''
ERR_FILE = ''

def get_response(url):
    for a in range(3):
        try:
            request = urllib.Request(url)
            response = urllib.urlopen(request)
            result = response.read()
            return result
        except Exception as e:
            print(e)
            time.sleep(2)
            continue

class ThreadCity(threading.Thread):
    def __init__(self, queue_zq_citys):
        threading.Thread.__init__(self)
        self.queue_zq_citys = queue_zq_citys
        self.spider = jd_spider.getSpider()

    def run(self):
        global UNSOLVED_FILE
        global SOLVED_FILE
        global ERR_FILE
        UNSOLVED_FILE = FILE_PATH + 'update_files/unsolved_' + 'cellphone' + '_urls.txt'
        SOLVED_FILE = FILE_PATH + 'update_files/solved_' +'cellphone'+ '_urls.txt'
        ERR_FILE = FILE_PATH + 'update_files/err_' +'cellphone'+ '_urls.txt'

        in_file = open(UNSOLVED_FILE, "r", encoding='utf-8')
        for each_line in in_file:
            url = each_line.strip("\n")
            try:
                html_data = self.spider.get_html(url)
                print(url+' html_data:'+str(html_data[0]))
                self.queue_zq_citys.put({'code': str(html_data[0])})
                time.sleep(1)
            except Exception as e:
                print('run err: '+str(e))
                pass


class ThreadCityDB(threading.Thread):
    def __init__(self, queue_zq_citys):
        threading.Thread.__init__(self)
        self.queue_zq_citys = queue_zq_citys

    def run(self):
        while True:
            try:
                if self.queue_zq_citys.empty():  # 队列为空
                    pass
                else:
                    citys = self.queue_zq_citys.get()  # 从队列中取出数据
                    if citys is not None:
                        sql = "insert into Table(cityid,cityname) values(%s,'%s')" % (
                            citys['cityid'], citys['cityname'])
                        # print  sql
                        DBHelper.SqlHelper.ms.ExecNonQuery(sql.encode('utf-8'))
                        self.queue_zq_citys.task_done()  # 告诉线程我完成了这个任务 是否继续join阻塞 让线程向前执行或者退出
                    else:
                        pass
            except Exception as e:
                pass


def main():
    try:
        queue_zq_citys = queue.Queue()  # 实例化存放抓取到的城市队列
        # 创建线程
        city = ThreadCity(queue_zq_citys)  # 抓取线程 入队操作
        # cityDB = ThreadCityDB(queue_zq_citys)  # 出队操作 存入数据库

        # 启动线程
        city.start()
        # cityDB.start()

        # 阻塞等待子线程执行完毕后再执行主线程
        city.join()
        # cityDB.join()
    except Exception as e:
        print('main err:'+str(e))
        pass

if __name__ == '__main__':
    main()