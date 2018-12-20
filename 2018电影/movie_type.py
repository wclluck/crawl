from pyecharts import TreeMap
import pandas as pd
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='maoyan', charset='utf8mb4')
cursor = conn.cursor()
sql = "select * from films"
db = pd.read_sql(sql, conn)

dom1 = []
for i in db['type']:
    type1 = i.split(',')
    for j in range(len(type1)):
        if type1[j] in dom1:
            continue
        else:
            dom1.append(type1[j])

dom2 = []
for item in dom1:
    num = 0
    for i in db['type']:
        type2 = i.split(',')
        for j in range(len(type2)):
            if type2[j] == item:
                num += 1
            else:
                continue
    dom2.append(num)


def message():
    for k in range(len(dom2)):
        data = {}
        data['name'] = dom1[k] + ' ' + str(dom2[k])
        data['value'] = dom2[k]
        yield data


data1 = message()
dom3 = []
for item in data1:
    dom3.append(item)

treemap = TreeMap("2018年电影类型分布图", title_pos='center', title_top='5', width=800, height=400)
treemap.add('2018年电影类型分布', dom3, is_label_show=True, label_pos='inside', is_legend_show=False)
treemap.render('2018年电影类型分布图.html')

