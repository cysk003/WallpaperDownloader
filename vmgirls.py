import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import urllib3
from multiprocessing import Pool, cpu_count

urllib3.disable_warnings()

save_path = path.join(os.environ['HOME'], 'Pictures', 'vmgirls')

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.vmgirls.com'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

ArticleTypes = [
    {'name': '摄影写真', 'url': '/photography', 'code': 17},  # 摄影写真
    {'name': '校园美女', 'url': '/campus', 'code': 33},  # 校园美女
    {'name': '清新美女', 'url': '/fresh', 'code': 25},  # 清新美女
    {'name': '清纯美女', 'url': '/pure', 'code': 18},  # 清纯美女
    {'name': '糖水', 'url': '/sweet', 'code': 61},  # 糖水
    {'name': '随笔', 'url': '/belles-lettres', 'code': 2},  # 随笔
    {'name': '青春风', 'url': '/youth', 'code': 12}  # 青春风
]


def get_articles(article_info: dict, page: int):
    res = []
    dst_url = base_url+'/wp-admin/admin-ajax.php'
    params = {
        'append': 'list-archive',
        'paged': page,
        'action': 'ajax_load_posts',
        'query': article_info['code'],
        'page': 'cat'
    }
    response = session.post(dst_url, data=params,
                            headers=headers, timeout=(3, 3))
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('a', class_='media-content', target='_blank')
        if articles:
            res = [{'title': article['title'], 'href': article['href']}
                   for article in articles]
    return res


def get_pics(article: dict):
    res = []
    response = session.get(article['href'], headers=headers, timeout=(3, 3))
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find('div', class_='nc-light-gallery')
        if div:
            pics = div.find_all('img', alt=True)
            res = [pic['data-src'] for pic in pics]
    return res


def get_pic_content(pic_url: str):
    response = session.get(pic_url, headers=headers, timeout=(3, 3))
    if response.status_code == 200:
        return response.content
    else:
        return None


def download(article: dict):
    pics = get_pics(article)
    dir_name = os.path.join(save_path, article['title'])
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if pics:
        for pic in pics:
            pic_name = pic.split('/')[-1]
            pic_path = os.path.join(dir_name, pic_name)
            if not os.path.exists(pic_path):
                content = get_pic_content(pic)
                if content:
                    with open(pic_path, 'wb+') as f:
                        f.write(content)
            else:
                print("{} already exists".format(pic_path))


if __name__ == "__main__":
    inf = ""
    index = 1
    for article_type in ArticleTypes:
        print("{}.{}".format(index, article_type['name']))
        index += 1
    inf += "\n请输入编号\n"
    i = int(input(inf)) - 1
    article_type = ArticleTypes[i]
    page = 1
    while(True):
        articles = get_articles(article_type, page)
        if articles:
            for article in articles:
                download(article)
                print(article)
        else:
            break
