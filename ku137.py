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


base_url = 'https://www.ku137.net/'
article_list_url = base_url + 'b/1/list_1_{}.html'
dir_name = 'ku137'
save_path = os.path.join(savepath.save_path, dir_name)


def get_articles(url):
    articles = []
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        response_content = response.content
        try:
            content = str(response_content, 'gb18030')
        except Exception as e:
            print(repr(e))
            try:
                content = str(response_content, 'utf-8')
            except Exception as e1:
                print(repr(e1))
                content = None
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            articles = [{'name': a['title'], 'href': a['href']}
                        for a in soup.select('div.m-list.ml1 > ul.cl > li > a')]
    return articles


def get_pics(url):
    pics = []
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        try:
            content = str(response.content, 'gb18030')
            soup = BeautifulSoup(content, 'html.parser')
            pics = [{'name': pic['src'].split('/')[-1], 'href': pic['src']}
                    for pic in soup.find_all('img', class_='tupian_img')]
        except Exception as e:
            print(repr(e))
            print(url)
    return pics


def get_zip(url):
    zip = None
    response = session.get(url, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        try:
            content = str(response.content, 'gb18030')
            soup = BeautifulSoup(content, 'html.parser')
            zip_a = soup.find('a', string='点击打包下载本套图')
            zip = {'name': zip_a['href'].split('/')[-1], 'href': zip_a['href']}
        except Exception as e:
            print(repr(e))
    return zip


def download(file_path, url):
    if path.exists(file_path):
        pass
        # print('{}已存在'.format(file_path))
    else:
        try:
            response = session.get(url, verify=False, timeout=(3, 3))
            if response.status_code == 200:
                with open(file_path, 'wb+') as f:
                    f.write(response.content)
                    # print('已下载到{}'.format(file_path))
        except Exception as e:
            print(repr(e))


download_zip = False


def download_article(article):
    print(article)
    global download_zip
    article_name = article['name'].strip()
    if article_name.endswith('.'):
        article_name = article_name[:-1]
    save_dir = path.join(save_path, article_name)
    if not path.exists(save_dir):
        try:
            os.makedirs(save_dir)
        except Exception as e:
            print(repr(e))
    article_href = article['href']
    article_url = article_href[0: -5] + '_{}.html'
    if download_zip:
        zip = get_zip(article_href)
        if zip:
            print('获取到zip包:{}'.format(zip))
            zip_name = zip['name']
            zip_href = zip['href']
            zip_file = path.join(save_dir, zip_name)
            if not savepath.check_exists(dir_name, article_name, zip_name):
                download(zip_file, zip_href)
    pics = get_pics(article_href)
    pic_page = 1
    while pics:
        for pic in pics:
            pic_name = pic['name']
            pic_href = pic['href']
            pic_file = path.join(save_dir, pic_name)
            if not savepath.check_exists(dir_name, article_name, pic_name):
                download(pic_file, pic_href)
        pic_page += 1
        pics = get_pics(article_url.format(pic_page))


num_str = input("您要从第几页开始？[默认1]")
if num_str.strip() == "":
    num = 1
else:
    try:
        num = int(num_str)
    except Exception as e:
        print("错误的数字！默认为1")
print("将要从第{}页开始下载！".format(num))
url = article_list_url.format(num)
articles = get_articles(url)
while articles:
    print("开始下载第{}页".format(num))
    pool = Pool(cpu_count() * 2)
    pool.map(download_article, articles)
    pool.close()
    pool.join()
    num += 1
    url = article_list_url.format(num)
    articles = get_articles(url)
