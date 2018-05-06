#!/usr/bin/python
# -*- coding:utf-8 -*-
import jieba.analyse
import numpy as np
import os

# hash操作
def string_hash(source):
    if source == "":
        return 0
    else:
        x = ord(source[0]) << 7
        m = 1000003
        mask = 2 ** 128 - 1
        for c in source:
            x = ((x * m) ^ ord(c)) & mask
        x ^= len(source)
        if x == -1:
            x = -2
        x = bin(x).replace('0b', '').zfill(64)[-64:]
        # print(source, x)  # 打印 （关键词，hash值）
        return str(x)

# 海明距离计算
def hammingDis(simhash1, simhash2):
    t1 = '0b' + simhash1
    t2 = '0b' + simhash2
    n = int(t1, 2) ^ int(t2, 2)
    i = 0
    while n:
        n &= (n - 1)
        i += 1
    return i

# 分词 权重 关键词 hash
def cal_simhash(text):
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("similarity_util.py")))) + '/data/').replace('\\','/')
    seg = jieba.cut(text)  # 分词
    jieba.analyse.set_stop_words(file_path+'procedure_files/stop_words.txt')  # 去除停用词
    keyWord = jieba.analyse.extract_tags( '|'.join(seg), topK=10, withWeight=True, allowPOS=())  # 先按照权重排序，再按照词排序
    # print(keyWord)  # 前20个关键词，权重
    keyList = []
    for feature, weight in keyWord:
        weight = int(weight * 10)
        feature = string_hash(feature)  # 对关键词进行hash
        temp = []
        for i in feature: # 将hash值用权值替代
            if (i == '1'):
                temp.append(weight)
            else:
                temp.append(-weight)
        keyList.append(temp)

    list_sum = np.sum(np.array(keyList), axis=0) # 20个权值列向相加
    # print( 'list_sum:', list_sum)  # 权值列向求和

    simhash = ''
    for i in list_sum:  # 权值转换成hash值
        if i > 0:
            simhash = simhash + '1'
        else:
            simhash = simhash + '0'
    # print ("simhash:"+simhash)  # str 类型
    return simhash

if __name__ == '__main__':
    text1 = '帮公司阿姨买的，他说还可以。'
    text2 = '帮老公买的，他很喜欢。'
    simhash1 = cal_simhash(text1)
    simhash2 = cal_simhash(text2)
    value = hammingDis(simhash1, simhash2)
    print(value)
    if value <= 3:
        print('Is Similar')
    else:
        print("Isn't Similar")