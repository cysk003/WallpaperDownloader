"""图集谷"""

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path
import savepath
from multiprocessing import Pool, cpu_count
import sys
sys.setrecursionlimit(1000000)

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.tujigu.com'
dir_name = '图集谷'
save_path = save_path = os.path.join(savepath.save_path, dir_name)


def download(url):
    for index in range(1, get_total_pages(url) + 1):
        real_url = url + '/' + str(index) + '.html' if index != 1 else url
        html = str(session.get(real_url, timeout=3).content, encoding='utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        download_collection(soup)


def d_collection(collection):
    tittle = collection.find_all('p', class_=['biaoti'])[
        0].text.strip().replace('<', '《').replace('>', '》')
    path = os.path.join(save_path, tittle)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            print(repr(e))
            return
    count_str = collection.find_all(
        'span', class_=['shuliang'])[0].text
    count = int(count_str[0: -1])
    print('共有' + str(count) + '张图片')
    img_url = collection.find_all('img')[0]['src']
    prefix = img_url[0: img_url.rfind('/')]
    # headers = {'Referer': collection.find_all('')}
    for num in range(1, count + 1):
        img_save_path = os.path.join(path, str(num) + '.jpg')
        if os.path.exists(img_save_path) or savepath.check_exists(dir_name, tittle, str(num) + '.jpg'):
            print('['+img_save_path + ']已存在')
            continue
        url = prefix + '/' + str(num) + '.jpg'
        try:
            content_response = session.get(url, timeout=3)
            if content_response.status_code == 200:
                content = content_response.content
                with open(img_save_path, 'wb') as f:
                    f.write(content)
                    f.close()
                    print('已下载[' + img_save_path + ']')
        except Exception as e:
            print(repr(e))
            continue


def download_collection(soup):
    all_collections = soup.find_all('div', class_=['hezi'])
    for x in all_collections:
        collections = x.find_all('ul')[0].find_all('li')
        pool = Pool(cpu_count() * 2)
        pool.map(d_collection, collections)
        pool.close()
        pool.join()


def get_total_pages(url):
    html = str(session.get(url, timeout=3).content, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all(id='pages')[0].find_all('a')[-2].text
    return int(pages)


def get_other_categories():
    html = str(session.get(base_url, timeout=3).content, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    categories = [(x.find_all('a')[0].text, x.find_all('a')[0]['href']) for x in soup.find_all(
        id='tag_ul')[0].find_all('li')]
    return categories


def download_other_categories():
    categories = get_other_categories()
    for name, url in categories:
        print('开始下载:' + name)
        html = str(session.get(url, timeout=3).content, encoding='utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        while soup:
            download_collection(soup)
            next_page_s = soup.find(id='pages').find(
                'a', class_='next', string='下一页')
            next_page = base_url + next_page_s['href'] if next_page_s else None
            html = str(session.get(next_page, timeout=3).content,
                       encoding='utf-8') if next_page else None
            soup = BeautifulSoup(html, 'html.parser') if html else None


if __name__ == "__main__":
    for cat in ['zhongguo', 'riben', 'hanguo', 'taiwan']:
        url = base_url + '/' + cat
        download(url)
    download_other_categories()
