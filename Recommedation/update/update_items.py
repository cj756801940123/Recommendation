#!/usr/bin/python
# -*- coding:utf-8 -*-
from Recommedation.common import item
from Recommedation.common import file_util
from Recommedation.database import database_util
from Recommedation.spider import html_analysis
from Recommedation.spider import jd_spider

import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')
UNSOLVED_FILE = ''
SOLVED_FILE = ''
ERR_FILE = ''

#获取待更新的url放进文件里
def get_urls_file(table):
    global UNSOLVED_FILE
    global SOLVED_FILE
    global ERR_FILE
    UNSOLVED_FILE = FILE_PATH+'update_files/unsolved_'+table+'_urls.txt'
    SOLVED_FILE = FILE_PATH+'update_files/solved_'+table+'_urls.txt'
    ERR_FILE = FILE_PATH+'update_files/err_'+table+'_urls.txt'

    sql = 'select distinct url from '+table;
    sql_results = database_util.search_sql(sql,None)
    if sql_results[0] == -1:
        return
    temp = list(sql_results[1])
    out_file = open(UNSOLVED_FILE, "w", encoding='utf-8')
    for j in temp:
        url =  list(j)[0]
        out_file.write(url + '\n')
    out_file.close()

    if os.path.exists(SOLVED_FILE):
        os.remove(SOLVED_FILE)

#打开那个全部都是链接的文件爬取每个商品的信息
def crawl_urls():
    file_util.del_solved_item(UNSOLVED_FILE,SOLVED_FILE)
    in_file = open(UNSOLVED_FILE, "r", encoding='utf-8')
    for each_line in in_file:
        url = each_line.strip("\n")
        print(url)
        if len(url) <= 0:
            break
        _item = item.getItem()
        _spider = jd_spider.getSpider()
        html_data = _spider.get_html(url)  # 获取商品详情页面的html数据
        # print(html_data)
        if html_data[0] == -1:
            print(html_data[1])
            continue
        # item = html_analysis.get_all_parameters(html_data, item)
        # item.price = spider.get_price(item.number)  # 获取商品的价格
        # if item.price == -1 or database_util.search_item(item.number) == 1:
        #     file = open(SOLVED_FILE, "a", encoding='utf-8')
        #     file.write(url + '\n')  # 把已经处理了的数据写进文件里面去
        #     file.close()
        #     continue
        # print("description：" + item.description)
        # print("price：%s" % str(item.price))
        # comment = spider.get_comments(FILE_PATH, str(item.number))
        # if comment == -1:
        #     continue
        # if database_handler.save_item(item, 'cellphones') != -1:
        #     file = open(FILE_PATH + 'procedure_files/solved_urls.txt', "a", encoding='utf-8')
        #     file.write(url + '\n')  # 把已经处理了的数据写进文件里面去
        #     file.close()
    in_file.close()


def test_urls(url):
    _spider = jd_spider.getSpider()
    html_data = _spider.get_html(url)  # 获取商品详情页面的html数据
    if html_data[0] == -1:
        print(html_data[1])


if __name__ == '__main__':
    table = 'cellphone'
    UNSOLVED_FILE = FILE_PATH+'update_files/unsolved_'+table+'_urls.txt'
    SOLVED_FILE = FILE_PATH+'update_files/solved_'+table+'_urls.txt'

    # get_urls_file('cellphone')
    crawl_urls()
    # test_urls('https://item.jd.com/6494556.html')
    #<urlopen error [WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。>
    #<urlopen error timed out>


