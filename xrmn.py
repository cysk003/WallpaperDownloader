import os
import re
import requests
import sys
from bs4 import BeautifulSoup
from matplotlib.pyplot import style, text
from requests.adapters import HTTPAdapter
from this import d

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = "https://www.xrmn5.com"
save_dir = '/run/media/liubodong/HDD3T_3/Pictures/xrmn'


def get_url_soup(url: str) -> BeautifulSoup:
    response = session.get(url=url, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        return BeautifulSoup(content, 'html.parser')
    return None


def get_all_modules() -> list[dict]:
    soup = get_url_soup(base_url)
    res = []
    for module_li in soup.select('ul.sub-menu > li > a'):
        res.append(
            {'module_href': base_url +
                            module_li['href'], 'module_title': module_li['title']}
        )
    return res


def get_all_article_indices(module: dict) -> list[str]:
    res = []
    module_href = module['module_href']
    list_soup = get_url_soup(module_href)
    page_div = list_soup.find('div', class_='page')
    last_page_a = page_div.find('a', text='尾页')
    max_page = int(last_page_a['href'].split('/')[-1].split('.')[0][5:])
    for index in range(1, max_page + 1):
        i = str(index)
        if index == 1:
            i = ''
        res.append(module_href + "index" + i + ".html")
    return res


def get_articles(article_index: str) -> list[dict]:
    res = []
    soup = get_url_soup(article_index)
    article_list_soup = soup.find(
        'ul', class_='update_area_lists cl').find_all('a')
    for a in article_list_soup:
        res.append({'article_title': a['title'],
                    'article_href': base_url + a['href']})
    return res


def get_article_imgs(article_url: str) -> list[str]:
    res = []
    soup = get_url_soup(article_url)
    pages = [base_url + page['href']
             for page in soup.select('div.page > a')[:-1]]
    for page in pages:
        soup = get_url_soup(page)
        p = soup.find('p', style='text-align: center')
        if not p:
            p = soup.find('p', align='center')
        imgs = [base_url + img['src'] for img in p.find_all('img')]
        res.extend(imgs)
    return res


def get_en(input: str) -> str:
    return ''.join(re.findall(r'[A-Za-z]', input))


def get_ku137_articles() -> dict:
    dict = {}
    for dir in os.listdir('/var/run/media/liubodong/HDD1T/ku137'):
        if dir.startswith('['):
            module_name = get_en(''.join(re.findall(r'^\[\S+\]', dir))).lower()
            if module_name:
                no = ''.join(re.findall(r'([NnOoVvLl]+\.[0-9]+)', dir))
                if no:
                    true_no = ''.join(re.findall(r'[0-9]+', no))
                    if true_no:
                        arr: list[str] = dict.get(module_name)
                        if not arr:
                            arr = []
                            dict[module_name] = arr
                        arr.append(true_no)
    return dict


ku137_articles = get_ku137_articles()

# 获取所有模块
modules = get_all_modules()
for module in modules:
    # 获取所有索引页
    article_indices = get_all_article_indices(module)
    for article_index in article_indices:
        # 获取每页所有主题
        article_list = get_articles(article_index)
        for article in article_list:
            article_title = article['article_title']
            article_href = article['article_href']

            save_path = os.path.join(save_dir, article_title)

            module_en = get_en(''.join(re.findall(r'^\[\S+\]', article_title))).lower()
            article_NO = ''.join(re.findall(r'([NnOoVvLl]+\.[0-9]+)', article_title))
            if article_NO:
                no = ''.join(re.findall(r'[0-9]+', article_NO))
                arr: list[str] = ku137_articles[module_en]
                if arr and no in arr:
                    print(article_title + " already exists in ku137")
                    continue

            # 获取主题下所有图片
            article_imgs = get_article_imgs(article_href)
            for img in article_imgs:
                img_name = img.split('/')[-1]
                pic_path = os.path.join(save_path, img_name)
                if os.path.exists(pic_path):
                    continue
                response = session.request('GET', img)
                if response.status_code == 200:
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    with open(pic_path, 'wb+') as f:
                        f.write(response.content)
                        f.flush()
                        f.close()
            print(article_title)
    #         break
    #     break
    # break
