#!/usr/bin/python
# -*- coding:utf-8 -*-
from Recommedation.analyse import sentiment_analysis
from Recommedation.common import file_util
import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

#这个要多线程
#有些评价换了行没有用户信息，需要处理让每一行都有用户信息
def add_comment_info(file_path):
    for sku_name in os.listdir(file_path):
        print(file_path+sku_name)
        line_list = []
        info = ''
        file = open(file_path+sku_name, "r", encoding='utf-8')
        for each_line in file:
            if each_line=='\n':
                continue
            index = each_line.find(' comment:')
            if index>=0:
                info = each_line[0:index+9]
                if each_line[index + 9:] == '\n':
                    continue
                each_line = each_line.strip("\n")
            else:
                each_line = (info+each_line).strip("\n")
            line_list.append(each_line)
        file.close()

        line_list = list(set(line_list))
        file = open(file_path+sku_name, "w", encoding='utf-8')
        for i in line_list:
            file.write(i + '\n')  # 把已经处理了的数据写进文件里面去
        file.close()

def load_attibute_word(file_name):
    fin = open(file_name, 'r', encoding='utf-8')  # 以读的方式打开文件
    attribute_words = []
    for eachLine in fin:
        word = eachLine.strip()
        words = word.split(',')
        temp = []
        for i in words:
            temp.append(i)
        attribute_words.append(temp)
    fin.close()
    return attribute_words

#这个要多线程
#筛选出有关键信息的评论
def filter_comment(in_path,out_path,attribute_words):
    FOUND = 0
    for sku_name in os.listdir(in_path):
        print(in_path + sku_name)
        in_file = open(in_path + sku_name, "r", encoding='utf-8')
        line_list = []

        for each_line in in_file:
            FOUND = 0
            for i in attribute_words:
                if FOUND ==1:
                    FOUND = 0
                    break
                for j in i:
                    if len(j)>0 and each_line.find(j) >= 0:
                        line_list.append(each_line)
                        FOUND =1
                        break
        in_file.close()

        out_file = open(out_path + sku_name, "w", encoding='utf-8')
        for i in line_list:
            out_file.write(i)
        out_file.close()

#文件里面有很多打分和实际评论不相符的评论，去掉那些不相符的评论
def filter_opposive_comment(word_file,file_name):
    fin = open(word_file, 'r', encoding='utf-8')  # 以读的方式打开文件
    words = []
    for eachLine in fin:
        words.append(eachLine.strip())
    fin.close()

    file = open(file_name, 'r', encoding='utf-8')  # 以读的方式打开文件
    line_list = []
    for each_line in file:
        bad = 0
        for i in words:
            if each_line.find(i)>=0:
                bad = 1
                break
        if bad == 0:
            line_list.append(each_line)

    fout = open(file_name, 'w', encoding='utf-8')  # 以写得方式打开文件
    for i in line_list:
        fout.write(i)
    fout.close()

def get_useful_comment(table):
    # 有些评价换了行没有用户信息，需要处理让每一行都有用户信息
    add_comment_info(DATA_PATH+table+'/item_comments/')
    add_comment_info(DATA_PATH+table+'/big_files/')
    add_comment_info(DATA_PATH+table+'/after_comments/')

    #把所有评价信息放进useful_comments里面去
    attribute_words = load_attibute_word(FILE_PATH + 'procedure_files/' + table + '_attributes.txt')
    in_path = DATA_PATH+table+'/item_comments/'
    out_path = DATA_PATH+table+'/useful_comments/'
    filter_comment(in_path,out_path,attribute_words)
    in_path = DATA_PATH+table+'/big_files/'
    filter_comment(in_path,in_path,attribute_words)

def filter_opppsive_comments(table):
    badword_file = FILE_PATH+'train_files/bad_words.txt'
    goodword_file = FILE_PATH+'train_files/good_words.txt'
    file_util.del_duplicate(badword_file)
    file_util.del_duplicate(goodword_file)
    filter_opposive_comment(badword_file,DATA_PATH + table + '/big_files/positive.txt')
    filter_opposive_comment(goodword_file,DATA_PATH + table + '/big_files/negative.txt')

if __name__ == '__main__':
    table = 'cellphone'
    get_useful_comment(table)
    filter_opppsive_comments(table)

    # add_comment_info(DATA_PATH + table + '/big_files/')
    # neg_file = file_path+'train_files/negative.txt'
    # pos_file = file_path+'train_files/positive.txt'
    # train_snowNLP(neg_file, pos_file)