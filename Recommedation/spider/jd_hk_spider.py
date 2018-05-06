#!/usr/bin/python
# -*- coding:utf-8 -*-
from urllib import request
from bs4 import BeautifulSoup as bs
import urllib
import json

class Spider:
    def checkCharset(self,url):
        resp = request.urlopen(url)
        html_data = resp.read()
        string = str(html_data)
        index1 = string.find('utf-8')
        index2 = string.find('UTF-8')
        if index1 >= 0 or index2>=0:
            return 1
        else:
            return 2

    def getPage(self,url):
        resp = request.urlopen(url)
        if self.checkCharset(url)==1 :
            html_data = resp.read().decode('utf-8','ignore')
        else:
            html_data = resp.read().decode('gbk', 'ignore')
        return html_data

    def getPageNum(self,page):
        soup = bs(page, 'html.parser')
        tag = soup.find('div',id="J_topPage")
        num = tag.span.i.get_text();
        return num

    def getDetailURL(self,page):
        soup = bs(page, 'html.parser')
        list = []
        products = soup.find_all('div',class_='p-name')
        count = 0
        for tag in products:
            if count>=3:
                list.append('https:'+tag.a.get('href'))
            count = count+1
        return list

    # 设置商品的全称
    def getDescription(self,soup,item):
        title = soup.find('div',id="spec-list",class_="spec-items").ul.find_all('li');
        if title[0].img==None:
            temp = str(title.get_text()).lstrip()
            temp = temp.rstrip()
            temp = temp.strip("'")
            temp = temp.strip('"')
            item.description = temp
        else:
            temp = str(title[0].img.get('alt')).lstrip()
            temp = temp.rstrip()
            temp = temp.strip("'")
            temp = temp.strip('"')
            item.description = temp
        return item

    # 设置图片的URL
    def getImgURL(self,soup,item):
        images = soup.find('div', id="spec-list", class_="spec-items").ul.find_all('li')
        count = 0;
        for i in images:
            if (count <= 4):
                if count == 0:
                    item.img1_address = 'https:' + str(i.img.get('src'))
                elif count == 1:
                    item.img2_address = 'https:' + str(i.img.get('src'))
                elif count == 2:
                    item.img3_address = 'https:' + str(i.img.get('src'))
                elif count == 3:
                    item.img4_address = 'https:' + str(i.img.get('src'))
                else:
                    item.img5_address = 'https:' + str(i.img.get('src'))
                count = count + 1
            else:
                break
        return item

    #获取好评率和评价总数
    def getProductComment(self,item):
        url = item.address
        id = url.split('/')[-1].strip(".html")
        url = 'https://club.jd.com/comment/productPageComments.action?&productId=' + id + '&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        jsondata = response.read().decode('gbk')
        data = json.loads(jsondata)
        item.good_comment_percentage = str(data['productCommentSummary']['goodRateShow'])+'%'
        item.comment_count = data['productCommentSummary']['commentCountStr']
        return item

    #获取商品的价格
    def getPriceByProxy(self,item):
        try:
            detail_url = item.address
            sku = detail_url.split('/')[-1].strip(".html")
            url = "https://p.3.cn/prices/mgets?skuIds=J_" + sku
            proxy_ip = {'http': '110.73.48.72:81238'}  # 想验证的代理IP
            proxy_support = urllib.request.ProxyHandler(proxy_ip)
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")]
            urllib.request.install_opener(opener)
            hjson = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
            item.price = float(hjson[0]['op'])
            return item
        except Exception as err:
            print(err)

    #获取商品的价格
    def getPrice(self,item):
        try:
            detail_url = item.address
            sku = detail_url.split('/')[-1].strip(".html")
            url = "https://p.3.cn/prices/mgets?skuIds=J_" + sku
            proxy_ip = {'https': '218.73.105.188:808'}  # 想验证的代理IP
            proxy_support = urllib.request.ProxyHandler(proxy_ip)
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")]
            urllib.request.install_opener(opener)
            hjson = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
            item.price = float(hjson[0]['op'])
            return item
        except Exception as err:
            print(err)

    #获取详细信息
    def getDetail(self,soup,item):
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
            if kind.find('编号')>=0:
                item.number = value
                continue
            if kind.find('毛重') >= 0:
                item.kg = value
                continue
            if kind.find('产地') >= 0:
                item.produce_address = value
                continue
            if kind.find('肤质') >= 0:
                item.good_for_skin = value
                continue
            if kind.find('人群') >= 0:
                item.good_for_who = value
                continue
            if kind.find('保质期') >= 0:
                item.expiration_date = value
                continue
            if kind.find('功效') >= 0:
                item.result_effectiveness = value
                continue
            if kind.find('分类') >= 0:
                item.category = value
                continue
            if kind.find('颜色') >= 0:
                item.color = value
                continue
            if kind.find('妆效') >= 0:
                item.makeup_effectiveness = value
                continue
            if kind.find('品牌') >= 0:
                item.brand = value
                continue
            if kind.find('防晒指数') >= 0:
                item.SPF = value
                continue
            if kind.find('PA值') >= 0:
                item.PA = value
                continue
        return item

    def getAttr(self,page,item,one,two,three):
        soup = bs(page, 'html.parser')
        item = self.getDescription(soup,item)
        item = self.getImgURL(soup,item)
        item = self.getProductComment(item)
        item = self.getDetail(soup,item)
        item.first_category = one
        item.second_category = two
        item.third_category = three
        return item


def getSpider():
    spider = Spider()
    return spider