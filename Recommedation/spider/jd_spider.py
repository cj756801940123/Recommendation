#!/usr/bin/python
# -*- coding:utf-8 -*-
import codecs
import json
import re
import requests
import urllib
import urllib.request
from Recommedation.spider import proxy_ip
import chardet
import jieba
import random
import time
import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

class Spider():
    def __init__(self):
        self.PROXY = {'http': '223.241.78.51:8118'}

    #爬取页面的信息，返回的是HTML格式的信息
    def get_html(self,url):
        for a in range(3):
            try:
                #1.创建一个代理处理器ProxyHandler
                proxy_support = urllib.request.ProxyHandler(self.PROXY)
                #2.创建和定制一个opener
                opener = urllib.request.build_opener(proxy_support)
                opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")]
                #3.安装和使用opener
                urllib.request.install_opener(opener)
                response = urllib.request.urlopen(url,timeout=5).read()

                # 获取页面的编码方式，然后才可以根据编码方式进行解码
                charset = chardet.detect(response)
                encoding = charset['encoding']
                # 根据页面编码方式进行解码，不然会乱码
                html_data = response.decode(encoding, 'ignore')
                return 0, html_data
            except Exception as err:
                print("get_html err: "+url+" "+str(err))
                time.sleep(2)
                continue
        return -1, str(err)

    # 获取商品的价格
    def get_price(self, sku):
        for a in range(2):
            try:
                url = "https://p.3.cn/prices/mgets?skuIds=J_" + sku
                proxy_support = urllib.request.ProxyHandler(self.PROXY)
                opener = urllib.request.build_opener(proxy_support)
                opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")]
                urllib.request.install_opener(opener)
                hjson = json.loads(urllib.request.urlopen(url,timeout=5).read().decode('utf-8'))
                return 0,float(hjson[0]['op'])
            except Exception as err:
                print("get_price err:" + sku + " " + str(err))
                self.PROXY = proxy_ip.get_proxy()
                time.sleep(2)
                continue
        return -1,'fail'

    def get_rate(self, file_path, sku):
        s = requests.session()
        url = 'https://club.jd.com/comment/productPageComments.action'
        data = {
            'callback': 'fetchJSON_comment98vv13933',
            'productId': sku,
            'score': 0,
            'sortType': 5,  # 评论按照什么排序：推荐排序和时间排序，默认5
            'page': 0,  # 当前是第几页评论，从0开始递增
            'pageSize': 10,  # 指定每一页展示多少评论，默认10
            'isShadowSku': 0,
            'fold': 1
        }
        sku_file = codecs.open(file_path + 'procedure_files/sloved_skus.txt', 'a', encoding='utf-8')
        rate_file = codecs.open(file_path + 'procedure_files/rate.txt', 'a', encoding='utf-8')
        try:
            t = s.get(url, params=data).text
            try:
                t = re.search(r'(?<=fetchJSON_comment98vv13933\().*(?=\);)', t).group(
                    0)  # fetchJSON_comment98vv13933(t的结果就是这里的内容)
            except Exception as e:
                print("no more page:" + str(e))
            j = json.loads(t)
            # print(j)
            comment_summary = j['productCommentSummary']
            good_rate = float(comment_summary['goodRate'])
            poor_rate = float(comment_summary['poorRate'])
            comment_count = int(comment_summary['commentCount'])
            list = []
            list.append(sku)
            list.append(good_rate)
            list.append(poor_rate)
            list.append(comment_count)
            list = str(list)
            print(list)
            rate_file.write(list + '\n')
            sku_file.write(sku + '\n')
        except Exception as e:
            print(e)
            return -1
        finally:
            sku_file.close()
            rate_file.close()
            return 1

    #获取每个商品的评论
    def get_comment(self,table,sku,page_no):
        s = requests.session()
        url = 'https://sclub.jd.com/comment/productPageComments.action'
        data = {
            'callback': 'fetchJSON_comment98vv13933',
            # 'callback': 'fetchJSON_comment98vv53129',
            'productId': sku,
            'score': 0,# 全部0、好评3、中评2、差评1、追评5，
            'sortType': 6,  # 评论按照什么排序：推荐排序5、时间排序6
            'page': 0,  # 当前是第几页评论，从0开始递增
            'pageSize': 10,  # 指定每一页展示多少评论，默认10
            'isShadowSku': 0,
            'fold': 1
        }
        #全部、好评：score=0，差评：score=1，追评：score=5
        item_file = codecs.open(DATA_PATH + table+'/item_comments/'+sku + '.txt', 'a', encoding='utf-8')
        pos_file = codecs.open(DATA_PATH + table+'/big_files/positive.txt', 'a', encoding='utf-8')
        neg_file = codecs.open(DATA_PATH + table+'/big_files/negative.txt', 'a', encoding='utf-8')
        for a in range(3):
            try:
                while True:
                    t = s.get(url, params=data,timeout=5).text
                    try:
                        t = re.search(r'(?<=fetchJSON_comment98vv13933\().*(?=\);)', t).group(0) #fetchJSON_comment98vv13933(t的结果就是这里的内容)
                    except Exception as e:
                        print("jd_spider get_comment first try err:"+str(e))
                        break
                    j = json.loads(t)
                    comment_summary = j['comments']
                    if comment_summary is None:
                        break
                    for comment in comment_summary:
                        # print(comment)
                        c_content = comment['content']  # 评论
                        score = comment['score']
                        name = comment['nickname']
                        if c_content.find( '此用户未填写评价内容')>=0:
                            continue
                        info = str(score) + ' nickname:' + name+' comment:'
                        if score > 4:
                            pos_file.write(info+c_content + '\n')
                        if score <=2:
                            neg_file.write(info+c_content + '\n')
                        item_file.write(info+c_content + '\n')
                    data['page'] += 1
                    page = data['page']
                    print('comment sku %s, comment page: %s'%(sku,str(page)))
                    if page>=page_no:
                        break
                item_file.close()
                pos_file.close()
                neg_file.close()
                return 0, 'success'
            except Exception as e:
                print('jd_spider get_comment err:sku %s, try %d time, %s'%(sku,a+1,str(e)))
                time.sleep(2)
                continue
        item_file.close()
        pos_file.close()
        neg_file.close()
        return -1, 'fail'

    #获取每个商品的追评
    def get_after_comment(self,table,sku,page_no):
        s = requests.session()
        url = 'https://sclub.jd.com/comment/productPageComments.action'
        data = {
            'callback': 'fetchJSON_comment98vv13933',
            # 'callback': 'fetchJSON_comment98vv53129',
            'productId': sku,
            'score': 5,# 全部0、好评3、中评2、差评1、追评5，
            'sortType': 6,  # 评论按照什么排序：推荐排序5、时间排序6
            'page': 0,  # 当前是第几页评论，从0开始递增
            'pageSize': 10,  # 指定每一页展示多少评论，默认10
            'isShadowSku': 0,
            'fold': 1
        }
        #全部、好评：score=0，差评：score=1，追评：score=5
        item_file = codecs.open(DATA_PATH + table+'/item_comments/'+sku + '.txt', 'a', encoding='utf-8')
        pos_file = codecs.open(DATA_PATH + table+'/big_files/positive.txt', 'a', encoding='utf-8')
        neg_file = codecs.open(DATA_PATH + table+'/big_files/negative.txt', 'a', encoding='utf-8')
        for a in range(3):
            try:
                while True:
                    t = s.get(url, params=data,timeout=5).text
                    try:
                        t = re.search(r'(?<=fetchJSON_comment98vv13933\().*(?=\);)', t).group(0) #fetchJSON_comment98vv13933(t的结果就是这里的内容)
                    except Exception as e:
                        print("jd_spider get_after_comment first try err:"+str(e))
                        break
                    j = json.loads(t)
                    comment_summary = j['comments']
                    if comment_summary is None:
                        break
                    for comment in comment_summary:
                        score = comment['score']
                        name = comment['nickname']
                        after_commet = comment['afterUserComment']['hAfterUserComment']['content']
                        info = str(score) + ' nickname:' + name+' comment:'
                        if score > 4:
                            pos_file.write(info+after_commet + '\n')

                        if score <= 2:
                            neg_file.write(info+after_commet + '\n')
                        item_file.write(info+after_commet+ '\n')
                    data['page'] += 1
                    page = data['page']
                    print('after_comment sku %s, comment page: %s'%(sku,str(page)))
                    if page>=page_no:
                        break
                item_file.close()
                pos_file.close()
                neg_file.close()
                return 0, 'success'
            except Exception as e:
                print('jd_spider get_after_comment err:sku %s, try %d time, %s'%(sku,a+1,str(e)))
                time.sleep(2)
                continue
        item_file.close()
        pos_file.close()
        neg_file.close()
        return -1, 'fail'

    def get_proxy_ip(self):
        proxy_ip_list = [
            {'https': '117.36.103.170: 8118'},#109天 2018/05/07
            {'https': '223.241.116.224:8010'},#119天 2018/05/07
            {'http': '61.135.217.7 :80'},#724天 2018/05/07
            {'http': '111.155.124.73:8123'},#649天 2018/05/07
            {'http': '223.241.78.51:8118'},#651天 2018/05/07
        ]
        self.PROXY = random.choice(proxy_ip_list)

if __name__== '__main__':
    # 5706773 / 6019534/ 5089225
    _spider = Spider()
    # spider.get_rate(FILE_PATH, '14102602376')
    # result = _spider.get_price('5706773')
    result = _spider.get_html('https://item.m.jd.com/product/20609148872.html ')
    #  https://item.jd.com/5716985.html
    print(result[0],result[1])
