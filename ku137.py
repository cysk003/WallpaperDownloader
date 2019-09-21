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


base_url = 'https://www.ku137.net/'
article_list_url = base_url + 'b/1/list_1_{}.html'
save_path = '/home/zodiac/Data/ku137'


def get_articles(url):
    articles = []
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'gbk')
        soup = BeautifulSoup(content, 'html.parser')
        articles = [{'name': a['title'], 'href': a['href']}
                    for a in soup.select('div.m-list.ml1 > ul.cl > li > a')]
    return articles


def get_pics(url):
    pics = []
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'gbk')
        soup = BeautifulSoup(content, 'html.parser')
        pics = [{'name': pic['src'].split('/')[-1], 'href': pic['src']}
                for pic in soup.find_all('img', class_='tupian_img')]
    return pics


def get_zip(url):
    zip = None
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'gbk')
        soup = BeautifulSoup(content, 'html.parser')
        zip_a = soup.find('a', string='点击打包下载本套图')
        zip = {'name': zip_a['href'].split('/')[-1], 'href': zip_a['href']}
    return zip


def dowload(file_path, url):
    if path.exists(file_path):
        print('{}已存在'.format(file_path))
    else:
        try:
            response = session.get(url, verify=False, timeout=(3, 3))
            if response.status_code == 200:
                with open(file_path, 'wb+') as f:
                    f.write(response.content)
                    print('已下载到{}'.format(file_path))
        except Exception as e:
            print(repr(e))


dowload_zip = False

num = 1
url = article_list_url.format(num)
articles = get_articles(url)
while articles:
    for article in articles:
        article_name = article['name']
        print('开始下载{}'.format(article_name))
        save_dir = path.join(save_path, article_name)
        if not path.exists(save_dir):
            os.makedirs(save_dir)
        article_href = article['href']
        article_url = article_href[0: -5] + '_{}.html'
        zip = get_zip(article_href)
        if zip and dowload_zip:
            print('获取到zip包:{}'.format(zip))
            zip_name = zip['name']
            zip_href = zip['href']
            zip_file = path.join(save_dir, zip_name)
            dowload(zip_file, zip_href)
        pics = get_pics(article_href)
        pic_page = 1
        while pics:
            for pic in pics:
                pic_name = pic['name']
                pic_href = pic['href']
                pic_file = path.join(save_dir, pic_name)
                dowload(pic_file, pic_href)
            pic_page += 1
            pics = get_pics(article_url.format(pic_page))
    num += 1
    url = article_list_url.format(num)
    articles = get_articles(url)