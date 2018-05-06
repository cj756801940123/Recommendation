#!/usr/bin/python
# -*- coding:utf-8 -*-
import pymysql
import os

def update_rate(file_path):
    try:
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,
                             charset="utf8")
        cur = db.cursor()  # 获取操作游标
        file = open(file_path + 'procedure_files/rate.txt', "r", encoding='utf-8')
        count = 1
        for each_line in file:
            line = each_line.strip('\n').split(',')
            line[0] = line[0].split('\'')[1]
            line[3] = int(line[3].split(']')[0])
            print(count, line)
            count += 1
            sql = "update cellphones set comment_count=%d, good_rate=%f ,poor_rate=%f where number='%s'" % (
            int(line[3]), float(line[1]), float(line[2]), line[0])
            cur.execute(sql)  # 执行sql语句
            # 提交到数据库执行
            db.commit()
    except Exception as err:
        print("fail to update database,err:" + str(err))
    finally:
        file.close()
        db.close()  # 关闭连接

def update_score(file_path):
    try:
        db = pymysql.connect(host="127.0.0.1", user="root", password="1234", db="recommendation", port=3306,charset="utf8")
        cur = db.cursor()  # 获取操作游标
        file = open(file_path + 'procedure_files/comment_scores.txt', "r", encoding='utf-8')
        count = 1
        for each_line in file:
            line = each_line.strip('\n').split(',')
            sku = line[0]
            print(count, line)
            count += 1
            sql = "update cellphones set screen =%f, speed=%f,touch=%f,appearance =%f, battery=%f," \
            "cost_effective =%f, delivery =%f,camera=%f,fingerprint=%f, experience=%f," \
            "effect =%f, screen =%f,quality=%f,genuine=%f,accessory =%f, " \
            "storage=%f,similarity=%f where number='%s'" %(
            round(float(line[1]),4),round(float(line[2]),4),round(float(line[3]),4),round(float(line[4]),4),round(float(line[5]),4),
            round(float(line[6]),4),round(float(line[7]),4), round(float(line[8]),4), round(float(line[9]),4), round(float(line[10]),4),
            round(float(line[11]),4), round(float(line[12]),4), round(float(line[13]),4), round(float(line[14]),4), round(float(line[15]),4),
            round(float(line[16]),4), round(float(line[17]),4), sku)

            cur.execute(sql)  # 执行sql语句
            db.commit()  # 提交到数据库执行

    except Exception as err:
        print("fail to update database,err:" + str(err))
    finally:
        file.close()
        db.close()  # 关闭连接

if __name__ == '__main__':
    file_path = (os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("add_score.py")))) + '/data/').replace('\\',                                                                                '/')
    update_score(file_path)

