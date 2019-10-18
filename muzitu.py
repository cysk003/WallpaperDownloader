# https://www.muzishan.com
# http://www.mmmjpg.com/

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import urllib3
import savepath
from multiprocessing import Pool, cpu_count

urllib3.disable_warnings()

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


base_url = 'https://www.muzishan.com'
dowload_url = 'https://i.muzishan.com'
dir_name = 'muzitu'
save_path = save_path = os.path.join(savepath.save_path, dir_name)


def escape(input_str):
    char_arr = '?!=()#%&$^*|\\;\'\".,:\t\n\r\b'
    input_str = input_str.strip()
    for char in char_arr:
        input_str = input_str.replace(char, '')
    return input_str


def get_total_pages():
    pages = 1
    response = session.get(base_url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        pages = int(soup.find('em', class_='info').string[1:-1])
    return pages


def get_articles(url):
    articles = []
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        for a in soup.select('ul > li > span > a'):
            name = a.string
            href = a['href']
            articles.append({'name': name, 'href': escape(href)})
    return articles


def download_article(article):
    print('开始下载[{}]'.format(article))
    article_name = article['name']
    save_dir = path.join(save_path, escape(article_name))
    if not path.exists(save_dir):
        os.makedirs(save_dir)
    article_href = article['href']
    article_id = article_href.split('/')[-1]
    num = 1
    pic_href = dowload_url + '/' + article_id + '/' + str(num) + '.jpg'
    try:
        response = session.get(pic_href,  verify=False, timeout=(3, 3))
        while response.status_code == 200:
            save_file = path.join(save_dir, str(num) + '.jpg')
            if not path.exists(save_file) and not savepath.check_exists(dir_name, escape(article_name), str(num) + '.jpg'):
                with open(save_file, 'wb+') as f:
                    f.write(response.content)
                    print('下载到' + save_file)
            else:
                print(save_file + '已存在')
            num += 1
            pic_href = dowload_url + '/' + article_id + '/' + str(num) + '.jpg'
            response = session.get(pic_href,  verify=False, timeout=(3, 3))
    except Exception as e:
        print(repr(e))


total_pages = get_total_pages()
for page in range(0, total_pages + 1):
    print('开始下载第{}页'.format(page + 1))
    if page == 0:
        articles = get_articles(base_url)
    else:
        articles = get_articles(base_url + '/home/' + str(page))
    pool = Pool(cpu_count() * 4)
    pool.map(download_article, articles)
    pool.close()
    pool.join()
