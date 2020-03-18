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


def get_soup(url):
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
            return soup
    return None


def get_articles(url):
    articles = []
    soup = get_soup(url)
    if soup:
        articles = [{'name': a['title'], 'href': a['href']}
                    for a in soup.select('div.m-list.ml1 > ul.cl > li > a')]
    return articles


def get_real_article_name(soup):
    real_articl_name = None
    if soup:
        line = soup.find('div', class_='position')
        if line:
            line_str = line.get_text()
            real_articl_name = line_str.split('>')[-1].strip()
    return real_articl_name


def get_pics(soup):
    pics = []
    if soup:
        try:
            pics = [{'name': pic['src'].split('/')[-1], 'href': pic['src']}
                    for pic in soup.find_all('img', class_='tupian_img')]
        except Exception as e:
            print(repr(e))
    return pics


def get_zip(soup):
    zip = None
    if soup:
        try:
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
    article_href = article['href']
    soup = get_soup(article_href)
    real_articl_name = get_real_article_name(soup)
    if real_articl_name:
        article_name = real_articl_name 
    else:
        article_name = article['name'].strip()
        if article_name.endswith('.'):
            article_name = article_name[:-1]
    save_dir = path.join(save_path, article_name)
    if not path.exists(save_dir):
        try:
            os.makedirs(save_dir)
        except Exception as e:
            print(repr(e))
    if download_zip:
        zip = get_zip(soup)
        if zip:
            print('获取到zip包:{}'.format(zip))
            zip_name = zip['name']
            zip_href = zip['href']
            zip_file = path.join(save_dir, zip_name)
            if not savepath.check_exists(dir_name, article_name, zip_name):
                download(zip_file, zip_href)
    pics = get_pics(soup)
    pic_page = 1
    article_url = article_href[0: -5] + '_{}.html'
    while pics:
        for pic in pics:
            pic_name = pic['name']
            pic_href = pic['href']
            pic_file = path.join(save_dir, pic_name)
            if not savepath.check_exists(dir_name, article_name, pic_name):
                download(pic_file, pic_href)
        pic_page += 1
        soup = get_soup(article_url.format(pic_page))
        pics = get_pics(soup)


def rename():
    num = 1
    url = article_list_url.format(num)
    articles = get_articles(url)
    while articles:
        for article in articles:
            s = get_soup(article['href'])
            real_articl_name = get_real_article_name(s)
            article_name = article['name'].strip()
            if article_name.endswith('.'):
                article_name = article_name[:-1]
            old_name = os.path.join(save_path, article_name)
            new_name = os.path.join(save_path, real_articl_name)
            if os.path.exists(old_name):
                os.rename(old_name, new_name)
        num += 1
        url = article_list_url.format(num)
        articles = get_articles(url)


num_str = input("您要从第几页开始？[默认1]\n输入0以重命名旧文件！")
if num_str.strip() == "":
    num = 1
else:
    try:
        num = int(num_str)
    except Exception as e:
        print("错误的数字！默认为1")

if num == 0:
    rename()
elif num > 0:
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
