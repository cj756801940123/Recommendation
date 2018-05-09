#!/usr/bin/python
# -*- coding:utf-8 -*-
import os

import jieba
import jieba.analyse
from snownlp import sentiment

from Recommedation.common import file_util, database_util

FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

#从数据库中获取品牌，用来扩充dictionary
def get_brand(table):
    dictionary = FILE_PATH + 'train_files/dictionary.txt'
    file = open(dictionary, "a", encoding='utf-8')
    brand1 = ''
    brand2 = ''
    try:
            sql = 'select distinct brand from ' + table
            result = list(database_util.search_sql(sql, None))
            if result[0] ==-1:
                return
            for j in result[1]:
                if len(j[0]) == 0:
                    continue
                line = j[0].strip()
                if line.find('（')>=0:
                    brand1 = line.split('（')[0]
                    brand2 = line.split('（')[1]
                    brand2 = brand2.split('）')[0]
                # file.write(brand1+ '\n'+brand2 + '\n')
                print(brand1,brand2)
    except Exception as err:
        print('tran_util get_brand err: %s'%(str(err)))
    finally:
        file.close()
    file_util.del_duplicate(dictionary)

def train_cut_word(file_name):
    dictionary = FILE_PATH + 'train_files/dictionary.txt'
    stop_words_file = FILE_PATH+'procedure_files/stop_words.txt'
    cut_file = FILE_PATH+'train_files/cut_words.txt'
    jieba.load_userdict(dictionary)
    jieba.analyse.set_stop_words(stop_words_file)  # 去除停用词

    stop_words = {}
    file = open(stop_words_file, 'r', encoding='utf-8')
    for each_word in file:
        stop_words[each_word.strip()] = each_word.strip()
    file.close()

    try:
        fout = open(cut_file, 'w', encoding='utf-8')
        fin = open(file_name, 'r', encoding='utf-8')
        for each_line in fin:
            index = each_line.find(' comment:')
            fout.write('\n')
            comment = each_line[index + 9:].strip('\n')
            word_List = list(jieba.cut(comment))  # 用结巴分词，对每行内容进行分词
            for word in word_List:
                if word not in stop_words and word not in dictionary:
                    fout.write(word+'\n')
    except Exception as e:
        print("fail in get_description,err:" + str(e))
    finally:
        fout.close()

#筛选出字数超过10个字的评价，用来训练snowNLP
def get_sentiment_file(file_name,out_file):
    line_list = []
    file = open(file_name, 'r', encoding='utf-8')
    for each_line in file:
        index = each_line.find(' comment:')
        if index >= 0:
            comment = each_line[index + 9:].strip('\n')
            if len(comment)>10:
                # print(comment)
                line_list.append(comment+'。')
    file.close()
    file = open(out_file, 'w', encoding='utf-8')
    for i in line_list:
        file.write(i)
    file.close()

#根据我处理好的训练数据，给snoNLP训练一下
def train_snowNLP(neg_file,pos_file,table):
    file_path = 'F:/computer_science/python3/lib/site-packages/snownlp/sentiment/'
    sentiment.train(neg_file, pos_file)
    sentiment.save(file_path+table+'.marshal')
    # 但是要把`snownlp/seg/__init__.py`里的`data_path`也改成你保存的位置，不然下次使用还是默认的。


#放一个评论文件给它训练一下，看看有哪些分词不正确的
def train_cut_word(file_name):
    dictionary = FILE_PATH + 'train_files/dictionary.txt'
    stop_words_file = FILE_PATH+'procedure_files/stop_words.txt'
    cut_file = FILE_PATH+'train_files/cut_words.txt'
    jieba.load_userdict(dictionary)
    jieba.analyse.set_stop_words(stop_words_file)  # 去除停用词

    stop_words = {}
    file = open(stop_words_file, 'r', encoding='utf-8')
    for each_word in file:
        stop_words[each_word.strip()] = each_word.strip()
    file.close()

    try:
        fout = open(cut_file, 'w', encoding='utf-8')
        fin = open(file_name, 'r', encoding='utf-8')
        for each_line in fin:
            index = each_line.find(' comment:')
            fout.write('\n')
            comment = each_line[index + 9:].strip('\n')
            word_List = list(jieba.cut(comment))  # 用结巴分词，对每行内容进行分词
            for word in word_List:
                if word not in stop_words and word not in dictionary:
                    fout.write(word+'\n')
    except Exception as e:
        print("fail in get_description,err:" + str(e))
    finally:
        fout.close()


if __name__ == '__main__':
    table = 'cellphone'
    get_brand(table)
    # train_cut_word(DATA_PATH+table+'/useful_comments/'+'19528027464.txt')

    get_sentiment_file(DATA_PATH+table+'/big_files/'+'positive.txt',FILE_PATH+'train_files/'+table+'_pos.txt')
    get_sentiment_file(DATA_PATH+table+'/big_files/'+'negative.txt',FILE_PATH+'train_files/'+table+'_neg.txt')

    neg_file = FILE_PATH+'train_files/'+table+'_neg.txt'
    pos_file = FILE_PATH+'train_files/'+table+'_pos.txt'
    train_snowNLP(neg_file, pos_file,table)






