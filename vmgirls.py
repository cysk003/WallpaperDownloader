import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import urllib3

urllib3.disable_warnings()

save_path = path.join(os.environ['HOME'], 'Pictures', 'vmgirls')

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.vmgirls.com'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}


def get_articles():
    res = []
    dst_url = base_url + '/sitemap.html'
    response = session.post(dst_url, headers=headers, timeout=(10, 10))
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        h3 = soup.find('h3', string="最新文章")
        articles = h3.find_next_sibling('ul')
        if articles:
            for article in articles.find_all('a', target='_blank'):
                res.append(
                    {'title': article['title'], 'href': base_url + '/' + article['href']})
    return res


def get_pics(article: dict):
    res = []
    response = session.get(article['href'], headers=headers, timeout=(10, 10))
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        div = soup.find('div', class_='nc-light-gallery')
        if div:
            pics = div.find_all('img', alt=True)
            res = [pic['data-src'] for pic in pics]
    return res


def get_pic_content(pic_url: str):
    response = session.get(pic_url, headers=headers, timeout=(10, 10))
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
    articles = get_articles()
    if articles:
        for article in articles:
            print(article)
            download(article)
