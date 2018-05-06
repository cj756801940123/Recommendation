#!/usr/bin/python
# -*- coding:utf-8 -*-
from Recommedation.spider import phone_item
from Recommedation.spider import jd_spider
from Recommedation.spider import html_analysis
from Recommedation.database import database_handler
import os

#获取商品的url，以便接下来进行处理
def get_urls(url,filename):
    spider = jd_spider.getSpider()
    html_data = spider.get_html(url)
    page_num = int(html_analysis.get_page_count(html_data))
    out_file = open(filename, "w",encoding='utf-8')
    for i in range(1,page_num+1):
        html_data = spider.get_html(url+ "&page=" + str(i))
        url_list = html_analysis.get_items_url(html_data)
        print('page:%s' % i)
        print(url_list)
        for i in url_list:
            out_file.write(i+'\n')
    out_file.close()

#把已经处理过的行从已处理文件中读出，然后从未处理的文件中去掉这些行
def del_solved_item(unsolve_file,solved_file):
    #获取所有的url
    all_urls = []
    file = open(unsolve_file, "r", encoding='utf-8')
    for each_line in file:
        url = each_line.strip("\n")
        if len(url) <= 0:
            break
        all_urls.append(url)
    file.close()

    #获取已经处理的url
    solved_urls = []
    try:
        file = open(solved_file, "r", encoding='utf-8')
    except:
        return

    for each_line in file:
        url = each_line.strip("\n")
        if len(url) <= 0:
            break
        solved_urls.append(url)
    file.close()

    file = open(unsolve_file, "w+", encoding='utf-8')
    file.truncate()

    for url in solved_urls:
        if url in all_urls:
            all_urls.remove(url)

    #把还没处理的url写回文件里面去
    file = open(unsolve_file, "w", encoding='utf-8')
    for url in all_urls:
        file.write(url+ '\n')
    file.close()

def print_item_parameters(item):
    print("address：" + item.address)
    print("description：" + item.description)
    print("price：%s" % str(item.price))
    print("img_url：" + item.img_address)
    print("brand：" + item.brand)
    print("name：" + item.name)
    print("number：" + item.number)
    print("operating_system：" + item.operating_system)
    print("ram：" + item.ram)
    print("rom：" + item.rom)
    print("get_time：%s\n" %str(item.get_time))

#打开那个全部都是链接的文件爬取每个商品的信息
def crawl_items(file_path):
    del_solved_item(file_path)
    in_file = open(file_path+'procedure_files/unsolved_urls.txt', "r", encoding='utf-8')
    for each_line in in_file:
        url = each_line.strip("\n")
        if len(url)<=0:
            break
        item = phone_item.getItem()
        spider = jd_spider.getSpider()
        html_data = spider.get_html(url)#获取商品详情页面的html数据
        if html_data == -1:
            continue
        item = html_analysis.get_all_parameters(html_data,item)
        item.price = spider.get_price(item.number) #获取商品的价格
        if item.price==-1 or database_handler.search_item(item.number)==1:
            file = open(file_path + 'procedure_files/solved_urls.txt', "a", encoding='utf-8')
            file.write(url + '\n')  # 把已经处理了的数据写进文件里面去
            file.close()
            continue
        print("address：" + item.address)
        print("description：" + item.description)
        print("price：%s" % str(item.price))
        comment = spider.get_comments(file_path, str(item.number))
        if comment ==-1:
            continue
        if database_handler.save_item(item, 'cellphones')!=-1:
            file = open(file_path + 'procedure_files/solved_urls.txt', "a", encoding='utf-8')
            file.write(url + '\n')#把已经处理了的数据写进文件里面去
            file.close()
    in_file.close()

#获取每个商品的好评率、差评率、评论总数
def crawl_rates(file_path):
    unsolved_file = file_path + 'procedure_files/unsolved_skus.txt'
    solved_file = file_path + 'procedure_files/solved_skus.txt'
    del_solved_item(unsolved_file,solved_file)

    in_file = open(file_path + 'procedure_files/unsolved_skus.txt', "r", encoding='utf-8')
    count = 1
    for each_line in in_file:
        sku = each_line.strip("\n")
        if len(sku) <= 0:
            break
        print(count)
        count += 1
        spider = jd_spider.getSpider()
        spider.get_rate(file_path,sku)
    in_file.close()

#获取商店的信息
def crawl_shop_info(file_path):
    unsolved_file = file_path + 'procedure_files/unsolved_skus.txt'
    solved_file = file_path + 'procedure_files/solved_skus.txt'
    del_solved_item(unsolved_file,solved_file)

    in_file = open(file_path + 'procedure_files/unsolved_skus.txt', "r", encoding='utf-8')
    count = 1
    shop_list = {}
    for each_line in in_file:
        sku = each_line.strip("\n")
        if len(sku) <= 0:
            break

        result = html_analysis.get_shop_info(sku, shop_list)
        if result==-1:
            continue
        shop_id = result[0]
        shop_name = result[1]
        follow_count = result[2]
        info = []
        info.append(shop_id)
        info.append(shop_name)
        info.append(follow_count)
        info.append(sku)
        shop_list[shop_id] = info
        # print(count, shop_list[result[0]])
        shop_info = sku+','+shop_id+','+shop_name+','+follow_count
        print(count, shop_info)

        file = open(file_path + 'procedure_files/shop_info.txt', "a", encoding='utf-8')
        file.write(shop_info + '\n')  # 把已经处理了的数据写进文件里面去
        file.close()

        file = open(file_path + 'procedure_files/solved_skus.txt', "a", encoding='utf-8')
        file.write(sku + '\n')  # 把已经处理了的数据写进文件里面去
        file.close()
        count += 1
    in_file.close()


def del_duplicate(file_path):
    url_list = []
    file = open(file_path+'procedure_files/unsolved_skus.txt', "r", encoding='utf-8')
    for each_line in file:
        url_list.append(each_line.strip("\n"))
    file.close()
    url_list = list(set(url_list))
    file = open(file_path + 'procedure_files/unsolved_skus.txt', "w", encoding='utf-8')
    for i in url_list:
        print(i)
        file.write(i + '\n')  # 把已经处理了的数据写进文件里面去
    file.close()


if __name__ == '__main__':
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("jd_search_product.py")))) + '/data/').replace('\\', '/')
    url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&wq=%E6%89%8B%E6%9C%BA&pvid=31a497b4f32548368033aeb5725a1336"
    # get_urls(url, file_path+'procedure_files/unsolved_urls.txt')
    # crawl_items(file_path)
    # del_duplicate(file_path)
    # crawl_rates(file_path)
    # crawl_shop_info(file_path)



