#!/usr/bin/python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import random
import urllib.request

def get_ip_list(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
    web_data = requests.get(url, headers=headers)
    soup = bs(web_data.text, 'html.parser')
    ips = soup.find_all('tr')
    proxy_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        alive_time = tds[8].text
        if alive_time.find('天')>0:#只要存活时间大于1天的
            ip = {}
            ip[tds[5].text] = tds[1].text + ':' + tds[2].text
            proxy_list.append(ip)
    return proxy_list

def test_proxy(proxy_list):
    if(len(proxy_list)==0):
        return "no proxy ip is available"
    proxy = random.choice(proxy_list)
    try:
        url = 'https://www.baidu.com/'
        proxy_support = urllib.request.ProxyHandler(proxy)
        opener = urllib.request.build_opener(proxy_support)
        opener.addheaders = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0")]
        urllib.request.install_opener(opener)
        urllib.request.urlopen(url).read()
    except Exception as e:
        print(e,proxy)
        proxy_list.remove(proxy)
        return -1,proxy_list
    else:
        return proxy,proxy_list

def get_avail_proxy(proxy_list):
    while True:
        result = test_proxy(proxy_list)
        if result[0] != -1:
            return result[0]
            break
        elif len(result[1])>0:
            proxy_list = result[1]
            print(proxy_list)
        else:
            break

def get_proxy():
    url = 'http://www.xicidaili.com/nn/'
    proxy_list = get_ip_list(url)
    avail_proxy = get_avail_proxy(proxy_list)
    return(avail_proxy)

if __name__ == '__main__':
    print(get_proxy())
