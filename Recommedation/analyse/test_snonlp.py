#!/usr/bin/python
# -*- coding:utf-8 -*-
from snownlp import SnowNLP
from snownlp import sentiment
from Recommedation.analyse import similarity_util
import re
import os

def test_sentiment(file_name):
    fin = open(file_name, 'r', encoding='utf-8')  # 以读的方式打开文件
    for eachLine in fin:
        # line = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", ",", eachLine)
        s = SnowNLP(eachLine)
        line = re.sub("[\s+\.\!\/_,$%^*()?;；【】+\"\']+|[+——！，;。？、~@#￥%……&*（）]+", ",", eachLine)
        whole_score = s.sentiments
        print(whole_score,line)
    fin.close()

if __name__ == '__main__':
    sentence = '这手机质量很好'
    s = SnowNLP(sentence)
    print(sentence,s.sentiments)

    sentence = '这手机一点都不耐电'
    s = SnowNLP(sentence)
    print(sentence,s.sentiments)

    # file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("snow_nlp.py")))) + '/data/').replace('\\','/')
    # neg_file = file_path+'train_files/neg.txt'
    # pos_file = file_path+'train_files/pos.txt'
    # train_snowNLP(neg_file, pos_file)
    # sentiment_analysis(file_path+'item_comments/5014204.txt',70,30)
    # test_sentiment(file_path+'train_files/train_result.txt')
    # sentiment_analysis(file_path + 'train_files/train_result.txt', 60, 40)


