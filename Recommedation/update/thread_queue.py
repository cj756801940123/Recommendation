#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
import queue
import threading
import time

from Recommedation.common import database_util
from Recommedation.common import item
from Recommedation.spider import html_analysis
from Recommedation.spider import jd_spider

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
        elif self.work[0] == 'get_comment':
            get_comment(self.queue, self.work[1],self.work[2])
        elif self.work[0] == 'update_score':
            update_score(self.name,self.queue, self.work[1],self.work[2])
        elif self.work[0] == 'insert_url':
            insert_url(self.name, self.queue, self.work[1])
        elif self.work[0] == 'get_param':
            get_param(self.name, self.queue, self.work[1])
        print("Exiting " + self.name)

def fill_queue(work_list):
    # 填充队列
    global QUEUE_LOCK
    global WORK_QUEUE
    QUEUE_LOCK.acquire()
    for work in work_list:
        WORK_QUEUE.put(work)
    QUEUE_LOCK.release()

#work是参数，work[0]是执行的任务，work[1]是表名table
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
    EXIT_FLAG = 0

#获取商品url，放进数据库
def insert_url(thread_name, queue,table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                url = queue.get()
                QUEUE_LOCK.release()
                count = list(database_util.search_sql('select count(*) url from '+table+' where url=%s', url)[1])[0][0]
                if count==0:
                    sql = 'insert into '+table+' set url=%s'
                    database_util.update_sql(sql, url)
            except Exception as err:
                print('thread_queue update_price err:' + str(err))
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
                print(thread_name,url)
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
                    count = list(database_util.search_sql('select count(*) from shop where shop_id=%s', shop_id)[1])[0][0]
                    if count==0:
                        database_util.update_sql('insert into shop(shop_id) values(%s)',shop_id)
            except Exception as err:
                print(err)
                # print('thread_queue get_shop_id err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def get_param(thread_name, queue, table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                url = queue.get()
                QUEUE_LOCK.release()
                _item = item.Item()
                _spider = jd_spider.Spider()
                html_data = _spider.get_html(url)  # 获取商品详情页面的html数据
                if html_data[0] == -1:
                    continue
                sku = url.strip('https://item.jd.com/').strip('.html')
                _item = html_analysis.get_all_param(html_data[1], _item)#获取普通参数
                _item = _spider.get_rate(sku,_item)#获取跟评价有关的信息
                result = _spider.get_price(sku)
                if result[0]!=-1:
                    _item.price = result[1]
                _item.price_times = 1

                print(thread_name,url)
                sql = 'update ' + table + ' set description=%s,price=%s,img=%s,brand=%s,name=%s,update_time=%s,' \
                      'comment=%s,rate=%s,max_price=%s,min_price=%s,avg_price=%s,price_times=%s,update_price_time=%s,update_rate_time=%s where sku=%s '
                data = [_item.description, _item.price, _item.img, _item.brand, _item.name, _item.update_time,
                        _item.comment, _item.rate,_item.price, _item.price, _item.price,1,_item.update_price_time,_item.update_rate_time,sku]
                database_util.update_sql(sql, data)
            except Exception as err:
                print('thread_queue get_param err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def get_comment(queue, table,page_no):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                sku = queue.get()
                QUEUE_LOCK.release()
                _spider = jd_spider.Spider()
                result = _spider.get_comment(table,sku,page_no)
                # if result[0] != -1:
                #     result = _spider.get_after_comment(table,sku,page_no)
                if result[0] != -1:
                    sql = 'update ' + table + ' set update_comment_time=%s where sku=%s '
                    data = [datetime.datetime.now(),sku]
                    database_util.update_sql(sql, data)
            except Exception as err:
                print('thread_queue get_comment err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def update_score(thread_name,queue,table,para):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                sku = queue.get()
                QUEUE_LOCK.release()
                w_rate = para['w_rate']
                w_follow = para['w_follow']
                w_comment = para['w_comment']
                w_sentiment = para['w_sentiment']
                w_brand = para['w_brand']

                sql = 'select sku,rate,follow,comment,sentiment,brand_hot from ' + table+' where sku=%s'
                result = database_util.search_sql(sql, sku)
                if result[0] != -1:
                    result = list(result[1])
                    for i in result:
                        sku = i[0]
                        rate = float(i[1]) * 100
                        follow = int(i[2])
                        comment = int(i[3])
                        sentiment = int(i[4])
                        brand_hot = int(i[5])
                        score = round((rate * w_rate + follow * w_follow + comment * w_comment + sentiment * w_sentiment + brand_hot* w_brand), 2)
                        sql = 'update ' + table + ' set score=%s where sku=%s'
                        data = [score, sku]
                        database_util.update_sql(sql, data)

            except Exception as err:
                print('thread_queue update_score err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def update_price(thread_name, queue, table):
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
                if price_result[0] != -1:
                    cur_price = price_result[1]
                    if cur_price > max_price:
                        max_price = cur_price
                    if cur_price < min_price:
                        min_price = cur_price
                    avg_price = round((avg_price * price_times + cur_price) / (price_times + 1), 2)
                    price_times += 1
                    print("%s: %.2f, %.2f, %.2f, %.2f" % (thread_name, max_price, min_price, avg_price, cur_price))
                    sql = 'update ' + table + ' set update_price_time=%s,max_price=%s,min_price=%s,avg_price=%s,price=%s,price_times=%s where sku=%s '
                    data = [datetime.datetime.now(), max_price, min_price, avg_price, cur_price, price_times, sku]
                    database_util.update_sql(sql, data)
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
                    if html_data[0] != -1:
                        result = html_analysis.get_shop_info(html_data[1])
                    else:
                        pass
                    if result[0] != -1:
                        follow = result[1]
                        shop_name = result[2]
                        print("%s: %s %d " % (thread_name, shop_name, follow))
                        sql = 'update shop set update_time=%s,follow=%s,shop_name=%s where shop_id=%s '
                        data = [datetime.datetime.now(), follow, shop_name, shop_id]
                        database_util.update_sql(sql, data)
                except Exception as err:
                    print('thread_queue update_shop_info err:' + str(err))
            else:
                QUEUE_LOCK.release()
            time.sleep(1)


if __name__ == '__main__':
    use_threading('update_price')