#!/usr/bin/python
# -*- coding:utf-8 -*-
import queue
import threading
from Recommedation.spider import jd_spider
from Recommedation.spider import html_analysis
from Recommedation.database import database_util
import time
import datetime

QUEUE_LOCK = threading.Lock()
WORK_QUEUE = queue.Queue()
EXIT_FLAG = 0

class MyThread(threading.Thread):
    def __init__(self, threadID, name, queue,work):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.queue = queue
        self.work = work

    def run(self):
        print("Starting " + self.name)
        if self.work[0] == 'update_price':
            update_price(self.name, self.queue,self.work[1])
        elif self.work[0] == 'update_shop_info':
            update_shop_info(self.name, self.queue,self.work[1])
        elif self.work[0] == 'get_shop_id':
            get_shop_id(self.name, self.queue,self.work[1])
        print("Exiting " + self.name)

def fill_queue(work_list):
    # 填充队列
    global QUEUE_LOCK
    global WORK_QUEUE
    QUEUE_LOCK.acquire()
    for work in work_list:
        WORK_QUEUE.put(work)
    QUEUE_LOCK.release()

def update_price(thread_name, queue,table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                data = queue.get()
                QUEUE_LOCK.release()
                sku = data['sku']
                max_price = data['max_price']
                min_price = data['min_price']
                avg_price = data['avg_price']
                price_times = data['price_times']
                _spider = jd_spider.Spider()
                price_result = _spider.get_price(sku)
                if price_result[0]!=-1:
                    cur_price = price_result[1]
                    if cur_price>max_price:
                        max_price = cur_price
                    if cur_price<min_price:
                        min_price = cur_price
                    avg_price = (avg_price*price_times+cur_price)/(price_times+1)
                    price_times +=1
                    print("%s: %f, %f, %f, %f" % (thread_name,max_price,min_price,avg_price, cur_price))
                    sql = 'update '+table+' set update_price_time=%s,max_price=%s,min_price=%s,avg_price=%s,price=%s,price_times=%s where sku=%s '
                    data = [ datetime.datetime.now(),max_price,min_price,avg_price,cur_price,price_times,sku]
                    database_util.update_sql(sql,data)
            except Exception as err:
                print('thread_queue update_price err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def update_shop_info(thread_name, queue, table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                shop_id = queue.get()
                QUEUE_LOCK.release()
                _spider = jd_spider.Spider()
                url = 'https://shop.m.jd.com/?shopId=' + shop_id
                print(url)
                html_data = _spider.get_html(url)
                if html_data[0]!=-1:
                    result = html_analysis.get_shop_info(html_data[1])
                else:
                    pass
                if result[0] != -1:
                    follow_count = result[1]
                    shop_name = result[2]
                    print("%s: %s %d " % (thread_name,shop_name,follow_count))
                    sql = 'update ' + table + ' set update_shop_time=%s,follow_count=%s,shop_name=%s where shop_id=%s '
                    data = [datetime.datetime.now(),follow_count,shop_name, shop_id]
                    database_util.update_sql(sql, data)
            except Exception as err:
                print('thread_queue update_shop_info err:'+str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def get_shop_id(thread_name, queue, table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                sku = queue.get()
                QUEUE_LOCK.release()
                url = 'https://item.m.jd.com/product/' + sku + '.html'
                _spider = jd_spider.Spider()
                html_data = _spider.get_html(url)
                if html_data[0] != -1:
                    result = html_analysis.get_shop_id(html_data[1])
                else:
                    pass
                if result[0] != -1:
                    shop_id = result[1]
                    print("%s: shop_id %s" % (thread_name, shop_id))
                    sql = 'update ' + table + ' set shop_id=%s where sku=%s '
                    data = [shop_id,sku]
                    database_util.update_sql(sql, data)
            except Exception as err:
                print('thread_queue get_shop_id err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)
    
def use_threading(work):
    global EXIT_FLAG
    THREAD_LIST = ["Thread-1", "Thread-2", "Thread-3","Thread-4"]
    threads = []
    threadID = 1

    # 创建新线程
    for thread_name in THREAD_LIST:
        thread = MyThread(threadID, thread_name, WORK_QUEUE,work)
        thread.start()
        threads.append(thread)
        threadID += 1

    # 等待队列清空
    while not WORK_QUEUE.empty():
        pass

    # 通知线程是时候退出
    EXIT_FLAG = 1

    # 等待所有线程完成
    for t in threads:
        t.join()
    print("Exiting Main Thread")

if __name__ == '__main__':
    use_threading('update_price')