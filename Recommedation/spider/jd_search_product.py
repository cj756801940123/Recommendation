#!/usr/bin/python
# -*- coding:utf-8 -*-
from Recommedation.common import item
from Recommedation.spider import jd_spider
from Recommedation.spider import html_analysis
from Recommedation.common import database_util
from Recommedation.update import thread_queue
from Recommedation.update import update_items
import os

#第一步获取商品的url，以便接下来进行处理
def get_url(url,table):
    _spider = jd_spider.Spider()
    html_data = _spider.get_html(url)
    if html_data[0]==-1:
        return
    page_num = int(html_analysis.get_page_count(html_data[1]))
    for i in range(1,40):
        if i>page_num:
            break
        html_data = _spider.get_html(url+ "&page=" + str(i))
        if html_data[0]==-1:
            continue
        url_list = html_analysis.get_items_url(html_data[1])
        print('page:%s' % i)
        thread_queue.fill_queue(url_list)
    thread_queue.use_threading(['insert_url', table])

#第二步把url中的sku获取出来
def get_sku(table):
    sql = 'select url,id from ' + table
    result = database_util.search_sql(sql, None)
    if result[0] != -1:
        result = list(result[1])
        for i in result:
            sku = i[0].strip('https://item.jd.com/').strip('.html')
            id = i[1]
            sql = 'update ' + table + ' set sku=%s where id=%s'
            database_util.update_sql(sql, [sku, id])

#第三步获取商店的id
def get_shop_id(table):
    update_items.get_shop_id(table)

#第四步获取商店的信息
def get_shop_info():
    sql = 'SELECT shop_id FROM shop where update_time is null';
    result = database_util.search_sql(sql, None)
    shop_id = []
    if result[0]!=-1:
        id = list(result[1])
        for i in id:
            if i[0] is not None:
                shop_id.append(i[0])
            else:
                print("shop_id is null")
    thread_queue.fill_queue(shop_id)
    thread_queue.use_threading(['update_shop_info',table])

#把店铺关注人数少的商品删掉
def del_url(table):
    sql = 'delete from '+table+' where sku in (select a.sku from (select a.sku from '+table+' a,shop b where a.shop_id=b.shop_id and b.follow<10000) a)'
    database_util.update_sql(sql,None)

#爬取商品信息
def get_param(table):
    sql = 'SELECT url FROM '+table+' where update_time is null';
    result = list(database_util.search_sql(sql, None)[1])
    # result = [('https://item.jd.com/4335139.html',)]
    url_list = []
    for i in result:
        url_list.append(i[0])
    thread_queue.fill_queue(url_list)
    thread_queue.use_threading(['get_param',table])

if __name__ == '__main__':
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("jd_search_product.py")))) + '/data/').replace('\\', '/')
    url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA&pvid=31a497b4f32548368033aeb5725a1336"
    url = 'https://search.jd.com/Search?keyword=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&ev=244_73390%7C%7C73389%7C%7C73398%5E&psort=3&click=0'
    table = 'computer'
    # get_url(url,table)
    # get_sku(table)
    # get_shop_id(table)
    # get_shop_info()
    # del_url(table)
    get_param(table)



