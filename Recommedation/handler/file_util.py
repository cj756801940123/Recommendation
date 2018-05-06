#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
FILE_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py")))) + '/data/').replace('\\', '/')
DATA_PATH = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("database_util.py"))))) + '/RecommendData/').replace('\\', '/')

#文件去除重读行
def del_duplicate(relative_path):
    url_list = []
    file = open(file_path+relative_path, "r", encoding='utf-8')
    for each_line in file:
        url_list.append(each_line.strip("\n"))
    file.close()
    url_list = list(set(url_list))
    file = open(file_path+relative_path, "w", encoding='utf-8')
    for i in url_list:
        file.write(i + '\n')  # 把已经处理了的数据写进文件里面去
    file.close()

#把已经处理过的行从已处理文件中读出，然后从未处理的文件中去掉这些行
def del_solved_item(unsolve_file,solved_file):
    if not os.path.exists(solved_file):
        print("not exit:"+solved_file)
        return
    file = ''
    #获取所有的url
    unsolve = []
    try:
        file = open(unsolve_file, "r", encoding='utf-8')
        for each_line in file:
            url = each_line.strip("\n")
            if len(url) <= 0:
                break
            unsolve.append(url)
    except Exception as e:
        print('del_solved_item err:' + str(e))
        return
    finally:
        file.close()

    #获取已经处理的url
    solved = []
    try:
        file = open(solved_file, "r", encoding='utf-8')
        for each_line in file:
            url = each_line.strip("\n")
            if len(url) <= 0:
                break
            solved.append(url)
    except Exception as e:
        print('del_solved_item err:'+str(e))
        return
    finally:
        file.close()

    file = open(unsolve_file, "w+", encoding='utf-8')
    file.truncate()

    for url in solved:
        if url in unsolve:
            unsolve.remove(url)

    #把还没处理的url写回文件里面去
    file = open(unsolve_file, "w", encoding='utf-8')
    for url in unsolve:
        file.write(url+ '\n')
    file.close()
    os.remove(solved_file)

if __name__ == '__main__':
    print(FILE_PATH)
    print(DATA_PATH)
