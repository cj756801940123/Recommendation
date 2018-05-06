#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import jieba
import jieba.analyse
import re
from gensim.models import word2vec
from stanfordcorenlp import StanfordCoreNLP
from gensim import corpora, models, similarities

file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("keywords_util.py")))) + '/data/').replace('\\', '/')

#获取用户评论中的TopK个关键字
def topK_words(topK):
    content = open(file_path + "solved_comments/some_comments.txt", 'rb').read()
    tags = jieba.analyse.textrank(content, topK=topK,withWeight=False, allowPOS=('n', 'np','vn'))
    fout = open(file_path + "topK_words_temp.txt", 'w', encoding='utf-8')  # 以写的方式打开文件
    for word  in tags:
        fout.write(word+ '\n')  # 将结果写入到输出文件
    return tags

#根据topK words 找出跟这些词最接近的词汇
def get_similar_words(file_path):
    sentences=word2vec.Text8Corpus(file_path+"solved_comments/del_stop_words.txt")
    model=word2vec.Word2Vec(sentences, size=100)
    fin = open(file_path + 'procedure_files/topK_words.txt', 'r', encoding='utf-8')  # 以读的方式打开文件
    fout = open(file_path + 'procedure_files/attribute_words.txt', 'w', encoding='utf-8')  # 以写的方式打开文件
    for eachLine in fin:
        word = eachLine.strip()
        print('\n'+word + ':')
        words = []
        words.append(word)
        for i in model.most_similar(word):
            words.append(i[0])
        fout.write(','.join(words)+ '\n')
    fin.close()

#去停用词
def del_stopwords(in_file, out_file):
    # 把停用词做成字典
    stopwords = {}
    fstop = open(file_path+'procedure_files/stop_words.txt', 'r',encoding='utf-8')
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

#优化jieba的分词
def update_words():
    # jieba.load_userdict(file_path+'item_comments/stanford_cut_words.txt')
    jieba.suggest_freq(('很', '漂亮'), True)
    jieba.suggest_freq('杠杠的', True)
    jieba.suggest_freq('全面屏', True)

def cut_file(in_file,out_file):
    fin = open(in_file, 'r', encoding='utf-8')  # 以读的方式打开文件
    fout = open(out_file, 'w', encoding='utf-8')  # 以写得方式打开文件
    count = 1
    for eachLine in fin:
        line = eachLine.strip()
        if len(line)<=0:
            continue
        if count<=10000:
            fout.write(line+ '\n')  # 将分词好的结果写入到输出文件
        else:
            break
        count+=1
    fin.close()
    fout.close()
    pass

#用斯坦福的进行分词
def standford_cut_words():
    nlp = StanfordCoreNLP(r'D:/ComputerScience/ProgramsOfPython/Recommendation/lib/stanford-corenlp-full-2018-01-31/',lang='zh')
    fin = open(filePath+'item_comments/comments.txt', 'r', encoding='utf-8')  # 以读的方式打开文件
    fout = open(filePath+'item_comments/stanford_cut_words.txt', 'w', encoding='utf-8')  # 以写得方式打开文件
    for eachLine in fin:
        line = eachLine.strip()
        if not line=='':
            tags = nlp.pos_tag(line)
            for i in tags:
                fout.write(i[0] + ' '+i[1]+'\n')  # 将分词好的结果写入到输出文件
                print(i[0] + ' '+ i[1])
    fin.close()
    fout.close()

def get_comment_similarity(content1,content2,topK):
    tags1 = jieba.analyse.textrank(content1, topK=topK, withWeight=False)
    tags2 = jieba.analyse.textrank(content2, topK=topK, withWeight=False)
    print(tags1)
    print(tags2)

if __name__ == '__main__':
    get_similar_words()
    #update_words(filePath)
    # standford_cut_words(filePath)
    # cut_file(file_path+"solved_comments/solved_comments.txt", file_path+"solved_comments/some_comments.txt")
    # topKWords = topK_words(file_path, 50)
    # del_stopwords(file_path, file_path+"solved_comments/cut_stop_words.txt", file_path+"solved_comments/del_stop_words.txt")
    # get_similar_words(file_path)
    # get_comment_similarity(content1, content2, 10)

