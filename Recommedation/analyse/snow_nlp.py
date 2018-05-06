#!/usr/bin/python
# -*- coding:utf-8 -*-
from snownlp import SnowNLP
from snownlp import sentiment
from Recommedation.analyse import similarity_util
import re
import os

#文件里面有很多不好的评论，去掉那些不好的额评论，选取max_num行放进out_file里面去
def filter_comment(word_file,in_file,out_file,max_num):
    fin = open(file_path + 'procedure_files/'+word_file, 'r', encoding='utf-8')  # 以读的方式打开文件
    words = []
    for eachLine in fin:
        words.append(eachLine.strip())
    fin.close()

    fin = open(in_file, 'r', encoding='utf-8')  # 以读的方式打开文件
    fout = open(out_file, 'w', encoding='utf-8')  # 以写得方式打开文件
    count = 1
    for eachLine in fin:
        line = eachLine.strip()
        if len(line)<=0 or line.find('未填写评价内容')>=0:
            continue
        if count>max_num:
            break
        bad = 0
        for i in words:
            if line.find(i)>=0:
                bad = 1
                break
        if bad == 0:
            fout.write(line+ '\n')  # 将分词好的结果写入到输出文件
            count+=1
    fin.close()
    fout.close()

#从评论信息中值选取关于那些attribute_words的词放进文件里面去，最多要max_num行
def get_train_file(attribute_words,in_file,out_file,max_num):
    fin = open(in_file, 'r', encoding='utf-8')  # 以读的方式打开文件
    fout = open(out_file, 'w', encoding='utf-8')  # 以写得方式打开文件
    try:
        count = 1
        for eachLine in fin:
            line = eachLine.strip()
            line = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", ",", line)
            sentences = line.split(',')
            for sentence in sentences:
                for i in attribute_words:
                    for j in i:
                        if len(j) > 0 and sentence.find(j) >= 0:
                            if count <= max_num:
                                fout.write(sentence + '\n')
                            else:
                                break
                            count += 1
    except Exception as e:
        print(e)
        return
    finally:
        fin.close()
        fout.close()

#把文件中的重复行删掉
def del_duplicate(in_file,out_file):
    url_list = []
    file = open(in_file, "r", encoding='utf-8')
    for each_line in file:
        url_list.append(each_line.strip("\n"))
    file.close()
    url_list = list(set(url_list))
    file = open(out_file, "w", encoding='utf-8')
    for i in url_list:
        print(i)
        file.write(i + '\n')
    file.close()

#根据我处理好的训练数据，给snoNLP训练一下
def train_snowNLP(neg_file,pos_file):
    file_path = 'F:/computer_science/python3/lib/site-packages/snownlp/sentiment/'
    sentiment.train(neg_file, pos_file)
    sentiment.save(file_path+'sentiment6.marshal')
    # 但是要把`snownlp/seg/__init__.py`里的`data_path`也改成你保存的位置，不然下次使用还是默认的。

#获取需要进行评分的属性词
def load_attibute_words(file_path):
    fin = open(file_path + 'procedure_files/attribute_words.txt', 'r', encoding='utf-8')  # 以读的方式打开文件
    attribute_words = []
    for eachLine in fin:
        word = eachLine.strip()
        words = word.split(',')
        temp = []
        for i in words:
            temp.append(i)
        attribute_words.append(temp)
    fin.close()
    # print(attributeWords)
    return attribute_words

#wight1是这句评价所占的权重，wight2是争端评价所占的权重
def sentiment_analysis(file_path,sku,wight1,wight2):
    attribute_words = load_attibute_words(file_path)
    comment_num = {}
    comment_score = {}
    for i in attribute_words:
        comment_num[i[0]] = 0
        comment_score[i[0]] = 0
    try:
        if os.path.exists(file_path+'item_comments/'+sku+'.txt'):
            fin = open(file_path+'item_comments/'+sku+'.txt', 'r', encoding='utf-8')  # 以读的方式打开文件
        else:
            fin = ''
            return
        long_comments = []
        long_comments_hash = []
        for eachLine in fin:
            # line = re.sub("[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", ",", eachLine)
            s = SnowNLP(eachLine)
            whole_score = s.sentiments
            line = re.sub("[\s+\.\!\/_,$%^*()?;；【】+\"\']+|[+——！，;。？、~@#￥%……&*（）]+", ",", eachLine)
            if len(line)>=30 and whole_score>=0.8:
                long_comments.append(line)
                long_comments_hash.append(similarity_util.cal_simhash(line))
                # print(whole_score,eachLine)
            sentences = line.split(',')
            for sentence in sentences:
                for i in attribute_words:
                    for j in i:
                        if len(j)>0 and sentence.find(j)>=0:
                            # if j.find('电')<0:
                            #     continue
                            s = SnowNLP(sentence)
                            score = s.sentiments
                            # print(sentence,(score*wight1+whole_score*wight2)/100)
                            comment_num[i[0]] += 1
                            comment_score[i[0]] += (score*wight1+whole_score*wight2)/100
                            break
    except Exception as e:
        print("sentiment_analysis failes,err:"+str(e))
        return
    finally:
        if fin != '':
            fin.close()

    for key in comment_score.keys():
        if (comment_num[key] > 0):
            comment_score[key] /= comment_num[key]

    num = len(long_comments_hash)
    sum = 0.0
    for i in range(0,num-1):
        for j in range(i+1,num):
            sim = similarity_util.hammingDis(long_comments_hash[i], long_comments_hash[j])
            sum += sim

    num = num*(num-1)/2
    similarity = 0
    if num>0:
        similarity = float(sum*1.0/num)
        print(similarity)
    comment_score['similarity'] = similarity

    print(comment_num)
    print(comment_score)
    return comment_score,attribute_words

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
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("snow_nlp.py")))) + '/data/').replace('\\','/')
    # neg_file = file_path+'train_files/neg.txt'
    # pos_file = file_path+'train_files/pos.txt'
    # train_snowNLP(neg_file, pos_file)
    # sentiment_analysis(file_path+'item_comments/5014204.txt',70,30)
    # test_sentiment(file_path+'train_files/train_result.txt')
    # sentiment_analysis(file_path + 'train_files/train_result.txt', 60, 40)


