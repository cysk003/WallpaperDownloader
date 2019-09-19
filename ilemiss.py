import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import urllib3

urllib3.disable_warnings()

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


base_url = 'https://www.ilemiss.net/'
save_path = '/home/zodiac/Data/ilemiss'

headers = {
    'Referer': None,
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
    'Accept': 'image/webp,*/*',
    'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

cookies = session.get(base_url, headers=headers,
                      verify=False, timeout=(3, 3)).cookies


def get_cat_pages(url):
    pages = 1
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        page = soup.find('div', class_='wlistpages').select('a:last-child')[0]
        if page.string == '尾页':
            pages = int(page['href'].split('/')[-1][0:-5].split('_')[-1])
    return pages


def get_articles(url):
    arr = []
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find_all('div', class_='imbtxt')
        for article in articles:
            a = article.find('a')
            name = a.string
            href = a['href']
            arr.append({'name': name, 'href': href})
    return arr


def get_article_pages(url):
    pages = 1
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        page = soup.find('div', class_='wlinkpages').select(
            'span:last-child')[0].find('a')
        if page.string == '尾页':
            pages = int(page['href'].split('/')[-1][0:-5].split('_')[-1])
    return pages


def get_pic(url):
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        pic = soup.find('div', class_='contentpic').find('img')
        href = pic['src']
        name = href.split('/')[-1]
        return {'name': name, 'href': href}
    else:
        return None


def dowload(cat):
    url = base_url + cat
    cat_pages = get_cat_pages(url)
    print('目录[' + cat + ']共有[' + str(cat_pages) + ']页')
    for cat_page in range(1, cat_pages + 1):
        print('开始下载第【' + str(cat_page) + '】页')
        if cat_page == 1:
            cat_url = url + '/'
        else:
            cat_url = url + '/index_' + str(cat_page) + '.html'
        articles = get_articles(cat_url)
        for article in articles:
            name = article['name']
            print('开始下载合集[' + name + ']')
            save_dir = path.join(save_path, name)
            if not path.exists(save_dir):
                os.makedirs(save_dir)
            article_href = article['href']
            article_href_head = article_href[0: -5]
            article_pages = get_article_pages(article_href)
            print('合集[' + name + ']共有[' + str(article_pages) + ']张图片')
            for article_page in range(1, article_pages + 1):
                if article_page != 1:
                    article_href = article_href_head + \
                        '_' + str(article_page) + '.html'
                pic = get_pic(article_href)
                if pic:
                    save_file = path.join(save_dir, pic['name'])
                    if path.exists(save_file):
                        print(save_file + ':已存在')
                    else:
                        try:
                            response = session.get(
                                pic['href'], headers=headers, verify=False, timeout=(3, 3))
                            if response.status_code == 200:
                                with open(save_file, 'wb+') as f:
                                    f.write(response.content)
                                    print('已下载' + save_file)
                        except Exception as e:
                            print('下载' + pic['href'] + '时出错')


cats = [
    {'name': '性感美女', 'value': 'sexy'},
    {'name': '清纯美女', 'value': 'mm'},
    {'name': '日本美女', 'value': 'japan'},
    {'name': '韩国美女', 'value': 'korea'},
    {'name': 'Cosplay', 'value': 'cosplay'},
    {'name': '动漫美女', 'value': 'dongman'}
]

for cat in cats:
    print('开始下载{}'.format(cat['name']))
    dowload(cat['value'])
