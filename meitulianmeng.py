import os
import requests
import urllib3
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count
from os import path
from requests.adapters import HTTPAdapter

import savepath

urllib3.disable_warnings()

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.meitulm.com/'
dir_name = 'meitulianmeng'
save_path = save_path = os.path.join(savepath.save_path, dir_name)

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


def get_articles(url):
    arr = []
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.find(
            'ul', class_='cat-one-list').find_all('div', class_='thimg')
        for article in articles:
            pic_num = article.find('span', class_='pic-num').string[0:-1]
            a = article.find('a')
            ele = {
                'name': a['title'],
                'href': a['href'],
                'num': pic_num
            }
            arr.append(ele)
    return arr


def get_pic(url):
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        pic = soup.find('div', class_='single-content').find('img')
        src = pic['src']
        if src:
            name = pic['src'].split('/')[-1]
            return {'name': name, 'href': pic['src']}
    return None


def download_article(article):
    name = article['name']
    print('开始下载:' + name)
    save_dir = path.join(save_path, name)
    if not path.exists(save_dir):
        os.makedirs(save_dir)
    pages = int(article['num'])
    for p in range(1, pages + 1):
        url = article['href'] + '?page=' + str(p)
        pic = get_pic(url)
        if pic:
            file_name = path.join(save_dir, pic['name'])
            if path.exists(file_name) or savepath.check_exists(dir_name, name, pic['name']):
                print(file_name + ':已存在')
            else:
                try:
                    response = session.get(
                        pic['href'], headers=headers, verify=False, timeout=(10, 10))
                    if response.status_code == 200:
                        with open(file_name, 'wb+') as f:
                            f.write(response.content)
                        print('下载到:' + file_name)
                except Exception as e:
                    print(repr(e))


num = 1
articles = get_articles(base_url + 'page_' + str(num) + '.html')
while articles:
    print('开始下载第[' + str(num) + ']页')
    # pool = Pool(cpu_count() * 2)
    # pool.map(download_article, articles)
    # pool.close()
    # pool.join()
    for article in articles:
        download_article(article)
    num += 1
    articles = get_articles(base_url + 'page_' + str(num) + '.html')
