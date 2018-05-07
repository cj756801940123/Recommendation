#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import datetime
import threading
import queue
from Recommedation.spider import jd_spider
from Recommedation.update import update_items

import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

UNSOLVED_FILE = ''
SOLVED_FILE = ''
ERR_FILE = ''

class CrawlThread(threading.Thread):
    def __init__(self, my_queue,unsolved_file):
        threading.Thread.__init__(self)
        self.my_queue = my_queue
        self.unsolved_file = unsolved_file
        self.spider = jd_spider.Spider()

    def run(self):
        in_file = open(UNSOLVED_FILE, "r", encoding='utf-8')
        for each_line in in_file:
            sku = each_line.strip("\n")
            try:
                html_data = self.spider.get_price(sku)
                self.my_queue.put({'code': str(html_data[0])})
                time.sleep(1)
            except Exception as e:
                print('run err: '+str(e))
                pass


class DataBaseThread(threading.Thread):
    def __init__(self, my_queue):
        threading.Thread.__init__(self)
        self.my_queue = my_queue

    def run(self):
        while True:
            try:
                if self.my_queue.empty():  # 队列为空
                    pass
                else:
                    citys = self.my_queue.get()  # 从队列中取出数据
                    if citys is not None:
                        sql = "insert into Table(cityid,cityname) values(%s,'%s')" % (
                            citys['cityid'], citys['cityname'])
                        # print  sql
                        # DBHelper.SqlHelper.ms.ExecNonQuery(sql.encode('utf-8'))
                        self.my_queue.task_done()  # 告诉线程我完成了这个任务 是否继续join阻塞 让线程向前执行或者退出
                    else:
                        pass
            except Exception as e:
                pass


def main():
    try:
        my_queue = queue.Queue()  # 实例化存放抓取到的城市队列
        # 创建线程
        in_queue = CrawlThread(my_queue)  # 抓取线程 入队操作
        out_queue = DataBaseThread(my_queue)  # 出队操作 存入数据库

        # 启动线程
        in_queue.start()
        out_queue.start()

        # 阻塞等待子线程执行完毕后再执行主线程
        in_queue.join()
        out_queue.join()
    except Exception as e:
        print('main err:'+str(e))
        pass

if __name__ == '__main__':
    main()