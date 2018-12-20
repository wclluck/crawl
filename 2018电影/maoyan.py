# coding:utf-8
import re
import time
import pymysql
import requests
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont


head ="""
Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Encoding:gzip, deflate, sdch
Accept-Language:zh-CN,zh;q=0.8
Cache-Control:max-age=0
Connection:keep-alive
Cookie:__mta=217430569.1543637280865.1543675194132.1543675269504.14; uuid_n_v=v1; uuid=A4971970F51E11E8A6B2DF1464BD270B9801DFC84D964F7B9543C0BEBAA3D138; _lxsdk_cuid=16767f41830c8-0bcdb64a3faefe-6b1b1279-100200-16767f41830c8; _lxsdk=A4971970F51E11E8A6B2DF1464BD270B9801DFC84D964F7B9543C0BEBAA3D138; _csrf=820a5f5d0dde447f1c773a540e21b00e1d7b516936021deb3772a86e3f8675ba; __mta=217430569.1543637280865.1543675269504.1543677892592.15; _lxsdk_s=1676a5f57e1-742-1f0-bce%7C%7C2
Host:maoyan.com
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"""


def str_to_dict(header):
    """
    构造请求头,可以在不同函数里构造不同的请求头
    """
    header_dict = {}
    header = header.split('\n')
    for h in header:
        h = h.strip()
        if h:
            k, v = h.split(':', 1)
            header_dict[k] = v.strip()
    return header_dict


def get_url():
    """
    获取电影详情页链接
    """
    for i in range(0, 300, 30):
        time.sleep(5)
        url = 'http://maoyan.com/films?showType=3&yearId=13&sortId=3&offset=' + str(i)
        host = 'Referer:http://maoyan.com/films?showType=3&yearId=13&sortId=3&offset=0'
        header = head + host
        headers = str_to_dict(header)
        response = requests.get(url=url, headers=headers)
        html = response.text



        #soup = BeautifulSoup(html, 'html.parser')
        soup = BeautifulSoup(html, 'lxml')
        data_1 = soup.find_all('div', {'class': 'channel-detail movie-item-title'})
        data_2 = soup.find_all('div', {'class': 'channel-detail channel-detail-orange'})
        num = 0
        #print(data_1)
        print("----------------------------------")
        #print(data_2)


        for item in data_1:
            num += 1
            time.sleep(10)
            #print(item)
            #print("bbbbbbbbbbb")
            #print(item.select('a'))
            url_1 = item.select('a')[0]['href']

            if data_2[num-1].get_text() != '暂无评分':
                url = 'http://maoyan.com' + url_1

                for message in get_message(url):
                    print(message)
                    to_mysql(message)
                #print(url)
                print('---------------^^^Film_Message^^^-----------------')
            else:
                print('The Work Is Done')
                break


def get_message(url):
    """
    获取电影详情页里的信息
    """
    time.sleep(10)
    data = {}
    host = """refer: http://maoyan.com/news
    """
    header = head + host
    headers = str_to_dict(header)
    response = requests.get(url=url, headers=headers)
    u = response.text
    #print("aaaaaaaaaaaaaaaaaaaaaaaaaa")
    #print(u)
    #print("bbbbbbbbbbbbbbbbbbbbbbbbbb")
    # 破解猫眼文字反爬
    (maoyan_num_list, utf8last) = get_numbers(u)
    # 获取电影信息

    #soup = BeautifulSoup(u, "html.parser")
    soup = BeautifulSoup(u, "lxml")
    mw = soup.find_all('span', {'class': 'stonefont'})
    score = soup.find_all('span', {'class': 'score-num'})
    unit = soup.find_all('span', {'class': 'unit'})
    ell = soup.find_all('li', {'class': 'ellipsis'})
    name = soup.find_all('h3', {'class': 'name'})
    # 返回电影信息
    data["name"] = name[0].get_text()
    data["type"] = ell[0].get_text()
    data["country"] = ell[1].get_text().split('/')[0].strip().replace('\n', '')
    data["length"] = ell[1].get_text().split('/')[1].strip().replace('\n', '')
    data["released"] = ell[2].get_text()[:10]
    # 因为会出现没有票房的电影,所以这里需要判断
    if unit:
        bom = ['分', score[0].get_text().replace('.', '').replace('万', ''), unit[0].get_text()]
        for i in range(len(mw)):
            moviewish = mw[i].get_text().encode('utf-8')
            moviewish = str(moviewish, encoding='utf-8')
            # 通过比对获取反爬文字信息
            for j in range(len(utf8last)):
                moviewish = moviewish.replace(utf8last[j], maoyan_num_list[j])
            if i == 0:
                data["score"] = moviewish + bom[i]
            elif i == 1:
                if '万' in moviewish:
                    data["people"] = int(float(moviewish.replace('万', '')) * 10000)
                else:
                    data["people"] = int(float(moviewish))
            else:
                if '万' == bom[i]:
                    data["box_office"] = int(float(moviewish) * 10000)
                else:
                    data["box_office"] = int(float(moviewish) * 100000000)
    else:
        bom = ['分', score[0].get_text().replace('.', '').replace('万', ''), 0]
        for i in range(len(mw)):
            moviewish = mw[i].get_text().encode('utf-8')
            moviewish = str(moviewish, encoding='utf-8')
            for j in range(len(utf8last)):
                moviewish = moviewish.replace(utf8last[j], maoyan_num_list[j])
            if i == 0:
                data["score"] = moviewish + bom[i]
            else:
                if '万' in moviewish:
                    data["people"] = int(float(moviewish.replace('万', '')) * 10000)
                else:
                    data["people"] = int(float(moviewish))
        data["box_office"] = bom[2]
    yield data



def to_mysql(data):
    """
    信息写入mysql
    """
    table = 'films'
    keys = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='maoyan',use_unicode=True, charset="utf8")
    cursor = db.cursor()
    sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
    try:
        if cursor.execute(sql, tuple(data.values())):
            print("Successful")
            db.commit()
    except Exception as err:
        print(err)
        print('Failed')
        db.rollback()
    db.close()


def get_numbers(u):
    """
    对猫眼的文字反爬进行破解
    """
    cmp = re.compile(",\n           url\('(//.*.woff)'\) format\('woff'\)")
    rst = cmp.findall(u)
    #print("aaaaaaaaaaaaaaaa")
    print(rst)
    ttf = requests.get("http:" + rst[0], stream=True)
    with open("maoyan.woff", "wb") as pdf:
        for chunk in ttf.iter_content(chunk_size=1024):
            if chunk:
                pdf.write(chunk)
    base_font = TTFont('base.woff')
    maoyanFont = TTFont('maoyan.woff')
    #print("fffffffffffffffffffff")
    print(maoyanFont)
    maoyan_unicode_list = maoyanFont['cmap'].tables[0].ttFont.getGlyphOrder()
    #print(maoyan_unicode_list)
    #print("gggggggggggggggggggggggggg")
    maoyan_num_list = []
    base_num_list = ['.', '3', '6', '2', '7', '8', '5', '4', '0', '9', '1']
    base_unicode_list = ['x', 'uniE00D', 'uniE7A8', 'uniF554', 'uniE3C4', 'uniF056', 'uniE214', 'uniF21D', 'uniE866', 'uniF1B3', 'uniEF3F']
    for i in range(1, 12):
        #print("hhhhhhhhhhhhhhhhhhhhhhhhh")
        maoyan_glyph = maoyanFont['glyf'][maoyan_unicode_list[i]]
        #print(maoyan_glyph)
        for j in range(11):
            base_glyph = base_font['glyf'][base_unicode_list[j]]
            if maoyan_glyph == base_glyph:
                maoyan_num_list.append(base_num_list[j])
                break
    maoyan_unicode_list[1] = 'uni0078'
    utf8List = [eval(r"'\u" + uni[3:] + "'").encode("utf-8") for uni in maoyan_unicode_list[1:]]
    utf8last = []
    for i in range(len(utf8List)):
        utf8List[i] = str(utf8List[i], encoding='utf-8')
        utf8last.append(utf8List[i])
    #print(maoyan_num_list)
    #print("cccccccccccccccccccccccccccccccccccc")
    #print(utf8last)
    return (maoyan_num_list, utf8last)


def main():
    time.sleep(5)
    get_url()


if __name__ == '__main__':
    main()
