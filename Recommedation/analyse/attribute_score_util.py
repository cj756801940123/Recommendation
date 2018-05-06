#!/usr/bin/python
# -*- coding:utf-8 -*-
from Recommedation.analyse import snow_nlp
import os


# 把已经处理过的行从已处理文件中读出，然后从未处理的文件中去掉这些行
def del_solved_item(unsolve_file, solved_file):
    # 获取所有的url
    all_urls = []
    file = open(unsolve_file, "r", encoding='utf-8')
    for each_line in file:
        url = each_line.strip("\n")
        if len(url) <= 0:
            break
        all_urls.append(url)
    file.close()

    # 获取已经处理的url
    solved_urls = []
    try:
        file = open(solved_file, "r", encoding='utf-8')
    except:
        return

    for each_line in file:
        url = each_line.strip("\n")
        if len(url) <= 0:
            break
        solved_urls.append(url)
    file.close()

    file = open(unsolve_file, "w+", encoding='utf-8')
    file.truncate()

    for url in solved_urls:
        if url in all_urls:
            all_urls.remove(url)

    # 把还没处理的url写回文件里面去
    file = open(unsolve_file, "w", encoding='utf-8')
    for url in all_urls:
        file.write(url + '\n')
    file.close()

def del_duplicate(file_name):
    url_list = []
    try:
        file = open(file_name, "r", encoding='utf-8')
        for each_line in file:
            url_list.append(each_line.strip("\n"))
        file.close()
        url_list = list(set(url_list))
        file = open(file_name, "w", encoding='utf-8')
        for i in url_list:
            # print(i)
            file.write(i + '\n')  # 把已经处理了的数据写进文件里面去
    except Exception as e:
        print("file not exit,err:"+str(e))
        return
    finally:
        file.close()

def get_score(file_path):
    unsolved_file = file_path + 'temp/unsolved_skus.txt'
    solved_file = file_path + 'temp/solved_skus.txt'
    del_duplicate(solved_file)
    del_solved_item(unsolved_file, solved_file)

    in_file = open(file_path + 'temp/unsolved_skus.txt', "r", encoding='utf-8')
    count = 1
    for each_line in in_file:
        sku = each_line.strip("\n")
        if len(sku) <= 0:
            break

        result = snow_nlp.sentiment_analysis(file_path,sku,80,20)
        if result is None:
            continue
        comment_scores = result[0]
        attibute_words = result[1]
        scores = []
        scores.append(sku)
        for i in attibute_words:
            # print(i[0])
            scores.append(comment_scores[i[0]])
        scores.append(comment_scores['similarity'])

        str_scores = ''
        for i in scores:
            str_scores = str_scores+str(i)+','
        print(count, str_scores)

        file = open(file_path + 'temp/comment_scores.txt', "a", encoding='utf-8')
        file.write(str_scores+ '\n')  # 把已经处理了的数据写进文件里面去
        file.close()

        file = open(file_path + 'temp/solved_skus.txt', "a", encoding='utf-8')
        file.write(sku + '\n')  # 把已经处理了的数据写进文件里面去
        file.close()
        count += 1
    in_file.close()


if __name__ == '__main__':
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("atribute_score_util.py")))) + '/data/').replace('\\','/')
    get_score(file_path)
    # neg_file = file_path+'train_files/neg.txt'
    # pos_file = file_path+'train_files/pos.txt'
    # train_snowNLP(neg_file, pos_file)