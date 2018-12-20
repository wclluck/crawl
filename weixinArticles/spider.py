from urllib.parse import urlencode
import pymongo
import requests
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
from config import *

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

base_url = 'http://weixin.sogou.com/weixin?'
headers = {
    'Cookie':'CXID=24726924BC5DF4733F26747AE11C77B0; SUV=009C7A5DB731034C58B238EDBE5AC630; ad=OEVsFyllll2Y1WFzlllllV0ckI6lllllJfkwukllllGlllllVllll5@@@@@@@@@@; SUID=95740EB76773860A582F1B390003F6AB; IPLOC=CN4403; ABTEST=7|1492776451|v1; SNUID=C2D684279095DD238A8F95DF90D05E5C; weixinIndexVisited=1; JSESSIONID=aaaT8qW5EcvX2_vYtdFSv; ppinf=5|1492789876|1493999476|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToyNzo',
    'Host' :'weixin.sogou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Mobile Safari/537.36'
}


proxy = None

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code ==200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url,count=1):
    print('Crawling',url)
    print('Trying Count',count)
    global proxy
    if count>=MAX_COUNT:
        print('Tired too many Counts')
        return None

    try:
        if proxy:
            proxies ={
                'http':'http://'+proxy
            }

            response = requests.get(url,allow_redirects=False,headers=headers,proxies=proxies)
        else:
            response = requests.get(url,allow_redirects=False,headers=headers)
        if response.status_code ==200:
            return response.text
        if response.status_code ==302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy',proxy)
               #count +=1
               #return get_html(url,count)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occured',e.args)
        proxy = get_proxy()
        count+=1
        return get_html(url,count)

def get_index(keyword,page):
    data = {
        'query' :KEYWORD,
        'type':2,
        'page':page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item  in items:
        yield item.attr('href')

def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#post-date').text()
        nickname = doc('#js_profile_qrcode > div > strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])


def main():
    for page in range(1, 101):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)

if __name__=='__main__':
    main()

