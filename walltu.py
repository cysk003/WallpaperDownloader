import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import savepath
from multiprocessing import Pool, cpu_count

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


base_url = 'https://www.walltu.com'
cat_url = base_url + '/mn'
dir_name = 'walltu'
save_path = save_path = os.path.join(savepath.save_path, dir_name)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
}

g_cookies = session.get(cat_url, headers=headers, timeout=(3, 3)).cookies


def escape(input_str):
    char_arr = '?!=()#%&$^*|\\;\'\".,:\t\n\r\b'
    input_str = input_str.strip()
    for char in char_arr:
        input_str = input_str.replace(char, '_')
    return input_str


def get_all_cats():
    response = session.get(cat_url, headers=headers, timeout=(3, 3))
    arr = []
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        all_cats = soup.find_all('p', id='q')
        for ele in all_cats:
            hrefs = ele.find_all('a')
            for href in hrefs:
                arr.append(
                    {'name': href.string, 'href': base_url + href['href']})
        return arr
    else:
        return None


def get_articles(cat):
    href = cat['href']
    arr = []
    response = session.get(href, headers=headers, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        article_list = soup.find('p', id='l').find_all('a')
        for article in article_list:
            name = article['title']
            article_href = article['href']
            arr.append({'name': name, 'href': base_url + article_href})
    return arr


def get_cat_total_pages(cat):
    pages = 1
    href = cat['href']
    response = session.get(href, headers=headers, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        page = soup.find('p', id='pg').select(
            'a:last-child')[0]['href'].split('.')[0].split('_')[-1]
        pages = int(page)
    return pages


def get_pics(article):
    href = article['href']
    href_head = href[0: -5]
    response = session.get(href, headers=headers, timeout=(3, 3))
    num = 1
    arr = []
    while response.status_code == 200:
        num += 1
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        try:
            pic_href = soup.find('dl', id='d').select('p > img')[0]['src']
        except Exception as e:
            print(repr(e))
            return arr
        pic_name = pic_href.split('/')[-1].split('!')[0]
        arr.append({'name': pic_name, 'href': pic_href, 'referer': href})
        href = href_head + '_' + str(num) + '.html'
        response = session.get(href, headers=headers, timeout=(3, 3))
    return arr


def download_article(article):
    global g_cookies
    print('开始下载:' + article['name'])
    save_dir = path.join(save_path, escape(article['name']))
    if not path.exists(save_dir):
        os.makedirs(save_dir)
    pics = get_pics(article)
    for pic in pics:
        save_file = path.join(save_dir, pic['name'])
        if path.exists(save_file) or savepath.check_exists(dir_name, escape(article['name']), pic['name']):
            print(save_file + ':已存在!')
        else:
            new_headers = {
                'Referer': pic['referer'],
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
                'Accept': 'image/webp,*/*',
                'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            try:
                response = session.get(
                    pic['href'], headers=new_headers, cookies=g_cookies, timeout=(10, 10))
                if response.status_code == 200:
                    cookies = response.cookies
                    with open(save_file, 'wb+') as f:
                        f.write(response.content)
            except Exception as e:
                print(repr(e))
                continue
            else:
                print('获取' + pic['href'] + '失败')


def downoad():
    cats = get_all_cats()
    for cat in cats:
        cat_href_head = cat['href'][0: -5]
        total_counts = get_cat_total_pages(cat)
        num = 1
        while num <= total_counts:
            if num == 1:
                articles = get_articles(cat)
            else:
                articles = get_articles(
                    {'name': cat['name'], 'href': cat_href_head + '_' + str(num) + '.html'})
            pool = Pool(cpu_count() * 4)
            pool.map(download_article, articles)
            pool.close()
            pool.join()
            num += 1


downoad()
