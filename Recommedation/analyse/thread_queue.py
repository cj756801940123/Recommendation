#!/usr/bin/python
# -*- coding:utf-8 -*-
from snownlp import SnowNLP
from Recommedation.analyse import similarity_util
from Recommedation.common import database_util
import queue
import threading
import time
import os
import re
import datetime
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

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
        if self.work[0] == 'get_unreal_comment':
            get_unreal_comment(self.name, self.queue,self.work[1])
        elif self.work[0] == 'get_sentiment_score':
            get_sentiment_score(self.name, self.queue,self.work[1])
        elif self.work[0] == 'del_unreal_comment':
            del_unreal_comment(self.name, self.queue,self.work[1])
        print("Exiting " + self.name)

def fill_queue(work_list):
    # 填充队列
    global QUEUE_LOCK
    global WORK_QUEUE
    QUEUE_LOCK.acquire()
    for work in work_list:
        WORK_QUEUE.put(work)
    QUEUE_LOCK.release()

def get_unreal_comment(thread_name, queue,table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                sku = queue.get()
                sku_name = sku+'.txt'
                QUEUE_LOCK.release()
                fin = open(DATA_PATH + table+'/useful_comments/'+ sku_name, 'r', encoding='utf-8')  # 以读的方式打开文件
                print(thread_name,sku_name)
                comments = []
                comments_hash = []
                unreal_comments = []
                for each_line in fin:
                    index = each_line.find(' comment:')
                    comment = each_line[index + 9:].strip('\n')
                    line = re.sub("[0-9a-zA-Z\s+\.\!\/_,$%^*()?;；【】+\"\']+|[+——！，;。？、~@#￥%……&*（）]+", ",", comment)
                    s = SnowNLP(line)
                    score = s.sentiments
                    if len(line) >= 30 and score >= 0.9:
                        # print(score,line)
                        comments.append(each_line.strip('\n'))
                        comments_hash.append(similarity_util.cal_simhash(line))

                num = len(comments_hash)
                solved = []
                for i in range(num):
                    solved.append(0)
                for i in range(0, num - 1):
                    if solved[i]==1:
                        continue
                    for j in range(i + 1, num):
                        sim = similarity_util.hammingDis(comments_hash[i],comments_hash[j])
                        if(sim<=5):
                            index = comments[i].find(' comment:')
                            info1 = comments[i][0:index + 9]
                            index = comments[j].find(' comment:')
                            info2 = comments[j][0:index + 9]
                            if info1==info2:
                                continue
                            print(thread_name,str(sim))
                            print(thread_name,comments[i])
                            print(thread_name,comments[j])
                            if solved[i]==0:
                                unreal_comments.append(str(sim)+' '+comments[i])
                                solved[i]=1;
                            unreal_comments.append(str(sim)+' '+comments[j])
                            solved[j]=1

                if len(unreal_comments)>0:
                    fout = open(DATA_PATH + table + '/unreal_comments/' + sku_name, 'w', encoding='utf-8')  # 以读的方式打开文件
                    for i in unreal_comments:
                        fout.write(i+'\n')
                    fout.close()

                sql = 'update '+table+' set update_unreal_time=%s where sku=%s '
                data = [ datetime.datetime.now(),sku]
                database_util.update_sql(sql, data)
            except Exception as err:
                print('analyse thread_queue get_unreal_comment err:' + str(err))
            finally:
                fin.close()
        else:
            QUEUE_LOCK.release()
        time.sleep(1)

def del_unreal_comment(thread_name, queue,table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                sku = queue.get()
                sku_name = sku+'.txt'
                QUEUE_LOCK.release()
                unreal_file = DATA_PATH + table+'/unreal_comments/'+ sku_name
                useful_file = DATA_PATH + table+'/useful_comments/'+ sku_name
                print(thread_name, sku_name)
                unreal = []
                try:
                    fout = open(unreal_file, 'a', encoding='utf-8')
                    fin = open(useful_file, 'r', encoding='utf-8')
                    for line in fin:
                        if line.find('宝贝')>=0:
                            fout.write('0 '+line)
                            print('0 '+line)
                            unreal.append(line)
                finally:
                    fin.close()
                    fout.close()

                if len(unreal) <= 0:
                    os.remove(unreal_file)

                if os.path.exists(unreal_file):
                    file = open(unreal_file, 'r', encoding='utf-8')
                    for line in file:
                        unreal.append(line[2:])
                    file.close()
                if len(unreal) > 0:
                    comments = []
                    try:
                        file = open(useful_file, 'r', encoding='utf-8')
                        for line in file:
                            if line not in unreal:
                                comments.append(line)
                    finally:
                        file.close()
                    try:
                        file = open(useful_file, 'w', encoding='utf-8')
                        for comment in comments:
                            file.write(comment)
                    finally:
                        file.close()
            except Exception as err:
                print('analyse thread_queue get_sentiment_score err:' + str(err))
        else:
            QUEUE_LOCK.release()
        time.sleep(1)


def get_sentiment_score(thread_name, queue,table):
    while not EXIT_FLAG:
        QUEUE_LOCK.acquire()
        if not WORK_QUEUE.empty():
            try:
                sku = queue.get()
                sku_name = sku+'.txt'
                QUEUE_LOCK.release()
                useful_file = DATA_PATH + table+'/useful_comments/'+ sku_name
                score_file = DATA_PATH + table+'/score_comments/'+ sku_name
                print(thread_name, sku_name)
                count = 0
                sum = 0
                file = open(useful_file, 'r', encoding='utf-8')
                fout = open(score_file, 'w', encoding='utf-8')
                score_list = []
                for each_line in file:
                    count+=1
                    index = each_line.find(' comment:')
                    comment = each_line[index + 9:].strip('\n')
                    s = SnowNLP(comment.strip('\n'))
                    score = int(s.sentiments*100)
                    score_comment = (str(score)+' '+each_line.strip('\n'))
                    print(score_comment)
                    sum += score
                    score_list.append(score_comment+'\n')
                for i in score_list:
                    fout.write(i)

                avg_acore = int(sum / count)
                print('%s %d' % (sku_name, avg_acore))

                sql = 'update ' + table + ' set sentiment=%s where sku=%s '
                data = [avg_acore, sku]
                database_util.update_sql(sql, data)
            except Exception as err:
                print('analyse thread_queue get_sentiment_score err:' + str(err))
            finally:
                file.close()
                fout.close()
        else:
            QUEUE_LOCK.release()
        time.sleep(1)


def use_threading(work):
    global EXIT_FLAG
    THREAD_LIST = ["Thread-1", "Thread-2", "Thread-3","Thread-4","Thread-5"]
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
    pass