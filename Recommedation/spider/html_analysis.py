#!/usr/bin/python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
import datetime
import re

# 获取这个类型的商品一共有多少页，用于后面获取其他页的商品url
def get_page_count(html_data):
    soup = bs(html_data, 'html.parser')
    tag = soup.find('div' ,id="J_topPage")
    num = tag.span.i.get_text();
    return num

# 根据首页获取每个具体商品的URL，用于后面对每个具体商品的搜索
def get_items_url(html_data):
    try:
        soup = bs(html_data, 'html.parser')
        list = []
        products = soup.find_all('div' ,class_='p-name')
        products2 = soup.find_all('div', class_='p-name p-name-type-2')
        for tag in products:
            if tag.a.get('href')[0 ] =='h':
                list.append(tag.a.get('href'))
            else:
                list.append('https:' + tag.a.get('href'))
        for tag in products2:
            if tag.a.get('href')[0] == 'h':
                list.append(tag.a.get('href'))
            else:
                list.append('https:' + tag.a.get('href'))
        return list
    except Exception as err:
        print('html_analysis get_items_url err:'+str(err))

# 区分是否属于全球购
def is_global(soup):
    try:
        div = soup.find('div', class_="crumb fl clearfix")
        kind = div.find_all('div', class_="item")
    except Exception as e:
        print("\n全球购")
        return 1
    else:
        print('\n京东购物')
        return 0

# 全球购获取商品详细信息
def get_param_global(soup,item):
    div = soup.find('div',class_ ="p-parameter")
    li = div.find('ul',class_="parameter2").find_all('li')
    for i in li:
        kind = i.get_text().split('：')[0]
        value = i.get_text().split('：')[1].lstrip(' ')
        value = value.strip("'")
        value = value.strip("'")
        if kind.find('名字') >= 0 or kind.find('名称') >= 0:
            item.name = value
            continue
        if kind.find('品牌') >= 0:
            item.brand = value
            continue
    return item

# 获取商品详细信息
def get_param(soup,item):
    div = soup.find('div',class_ ="p-parameter")
    li = div.find('ul', id="parameter-brand",class_="p-parameter-list").li
    item.brand = li.a.get_text()
    li = div.find('ul',class_="parameter2 p-parameter-list").find_all('li')
    for i in li:
        kind = i.get_text().split('：')[0]
        value = i.get_text().split('：')[1]
        value = value.strip("'")
        # value = value.strip("'")
        if kind.find('名字') >= 0 or kind.find('名称') >= 0:
            item.name = value
            continue
        if kind.find('品牌') >= 0:
            item.brand = value
            continue

    #获取商品的标题
    title = soup.find('div' ,class_ ="sku-name");
    if title. img ==None:
        temp = str(title.get_text()).lstrip()
        temp = temp.rstrip()
        temp = temp.strip("'")
        temp = temp.strip('"')
        item.description = temp
    else:
        temp = str(title.img.get_text()).lstrip()
        temp = temp.rstrip()
        temp = temp.strip("'")
        temp = temp.strip('"')
        item.description = temp

    #获取商品图片的链接
    images = soup.find('div', id="spec-list", class_="spec-items").ul.find_all('li')
    img = 'https:' + str(images[0].img.get('src'))
    item.img = img.replace('n5/s54x54_jfs', 'n7/jfs')
    return item

# 获取商品的各种信息，用它来调用其它的方法
def get_all_param(html_data,item):
    soup = bs(html_data, 'html.parser')
    if is_global(soup):
        item = get_param_global(soup, item)
    else:
        item = get_param(soup, item)
    item.update_time = datetime.datetime.now()
    item.update_price_time = datetime.datetime.now()
    item.update_rate_time = datetime.datetime.now()
    return item

# 获取店铺id
def get_shop_id(html_data):
    try:
        soup = bs(html_data, 'html.parser')
        div = soup.find_all('script')
        found = 0
        shop_id = ''
        for i in div:
            temp = str(i)
            if found==1:
                break
            index = temp.find('shopId')
            index2 = 0
            if index>=0:
                for j in range(index,index+20):
                    if temp[j]==',':
                        index2 = j
                        break
                shop_id = temp[index+8:index2]
                return 0, shop_id
            index = temp.find('venderID')

            if index>=0:
                for j in range(index+8,index+30):
                    if temp[j]==',':
                        index2 = j
                        break
                shop_id = temp[index+11:index2-1]
                return 0, shop_id
        if len(shop_id)==0:
            return -1,'fail'
        return 0,shop_id
    except Exception as e:
        print('get_shop_id err:'+str(e))
        return -1,'fail'

def get_shop_info(html_data):
    try:
        soup = bs(html_data, 'html.parser')
        div = soup.find('div', class_='cell shop-info')
        shop_name = div.find('span', class_='ui-flex shop-name').find('em').get_text()
        follow_num = div.find('span',class_='ui-flex shop-other').find('em').get_text()
        count = float(re.findall(r"\d+\.?\d*",follow_num)[0])
        if follow_num.find('万')>0:
            count = count*10000
        count = int(count)
        return 0,count,shop_name
    except Exception as e:
        print('html_analysis get_shop_info err:'+str(e))
        return -1,'fail'

if __name__ == '__main__':
    url = 'https://item.jd.com/21056257657.html'
    sku = '4586850'
    get_shop_info(sku)

