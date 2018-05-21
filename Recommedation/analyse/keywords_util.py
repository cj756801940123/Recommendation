#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import jieba
import jieba.analyse
import re
from gensim.models import word2vec
from stanfordcorenlp import StanfordCoreNLP
from gensim import corpora, models, similarities
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

#d第一步：获取用户评论中的TopK个关键字
def topK_words(table,topK):
    try:
        fin = open(DATA_PATH + table+"/big_files/positive.txt", 'r', encoding='utf-8')
        fout = open(DATA_PATH + table+ "/big_files/comments.txt", 'w', encoding='utf-8')
        for line in fin:
            index = line.find('comment:')
            comment = line[index+8:].strip('\n')
            fout.write(comment+',')
    except Exception as err:
        print(err)
    finally:
        fin.close()
        fout.close()

    del_stopwords(DATA_PATH + table+ "/big_files/comments.txt",DATA_PATH + table+ "/big_files/cut_comments.txt")
    os.remove(DATA_PATH + table+ "/big_files/comments.txt")
    content = open(DATA_PATH + table+ "/big_files/cut_comments.txt", 'rb').read()
    tags = jieba.analyse.textrank(content, topK=topK,withWeight=False, allowPOS=('n', 'np','vn'))
    print(tags)
    fout = open(FILE_PATH + "procedure_files/"+table+"_topK_words.txt", 'w', encoding='utf-8')  # 以写的方式打开文件
    for word  in tags:
        fout.write(word+ '\n')  # 将结果写入到输出文件
    return tags

#第二步：根据topK words 找出跟这些词最接近的词汇
def get_similar_words(table):
    sentences = word2vec.Text8Corpus(DATA_PATH + table+ "/big_files/cut_comments.txt")
    model = word2vec.Word2Vec(sentences, size=100)
    fin = open(FILE_PATH + 'procedure_files/'+table+'_topK_words.txt', 'r', encoding='utf-8')  # 以读的方式打开文件
    fout = open(FILE_PATH + 'procedure_files/'+table+'_attributes.txt', 'w', encoding='utf-8')  # 以写的方式打开文件
    for eachLine in fin:
        word = eachLine.strip()
        print('\n'+word + ':')
        words = []
        words.append(word)
        for i in model.most_similar(word):
            words.append(i[0])
        fout.write(','.join(words)+ '\n')
    fin.close()
    os.remove(FILE_PATH + 'procedure_files/'+table+'_topK_words.txt')

#去停用词
def del_stopwords(in_file, out_file):
    # 把停用词做成字典
    stopwords = {}
    fstop = open(FILE_PATH+'procedure_files/stop_words.txt', 'r',encoding='utf-8')
    for eachWord in fstop:
        stopwords[eachWord.strip()] = eachWord.strip()
    fstop.close()
    fin = open(in_file, 'r',encoding='utf-8')  # 以读的方式打开文件
    fout = open(out_file, 'w',encoding='utf-8')  # 以写得方式打开文件
    for eachLine in fin:
        line = eachLine.strip()
        line1 = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", "",line)
        wordList = list(jieba.cut(line1))  # 用结巴分词，对每行内容进行分词
        outStr = ''
        for word in wordList:
            if word not in stopwords:
                outStr += word
                outStr += ' '
        fout.write(outStr.strip()+ '\n')  # 将分词好的结果写入到输出文件
    fin.close()
    fout.close()

if __name__ == '__main__':
    table = 'computer'
    topK_words(table,50)
    get_similar_words(table)

