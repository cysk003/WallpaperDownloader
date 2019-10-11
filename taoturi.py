import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import urllib3
import savepath

urllib3.disable_warnings()

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


base_url = 'https://www.taoturi.com/'
save_path = save_path = os.path.join(savepath.save_path, 'taoturi')

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
            'div', class_='video-block section-padding').find_all('a', marked='1', target=False)
        for article in articles:
            arr.append({'name': article['title'],
                        'href': article['href']})
    return arr


def get_pic_pages(url):
    pages = 1
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        page = soup.find('ul', id='Pic_paging').select(
            'li:last-child')[0].find('a')
        if page.string == '尾页':
            pages = int(page['href'].split('?')[-1].split('=')[-1])
    return pages


def get_pic(url):
    response = session.get(url, headers=headers, verify=False, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        pic = soup.find('div', class_='post-body').find('img')
        src = pic['src']
        if src:
            name = pic['src'].split('/')[-1]
            return {'name': name, 'href': pic['src']}
    return None


num = 1
articles = get_articles(base_url + 'page_' + str(num) + '.html')
while articles:
    print('开始下载第[' + str(num) + ']页')
    for article in articles:
        name = article['name']
        print('开始下载:' + name)
        save_dir = path.join(save_path, name)
        if not path.exists(save_dir):
            os.makedirs(save_dir)
        pages = get_pic_pages(article['href'])
        for p in range(1, pages + 1):
            url = article['href'] + '?page=' + str(p)
            pic = get_pic(url)
            if pic:
                file_name = path.join(save_dir, pic['name'])
                if path.exists(file_name):
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
    num += 1
    articles = get_articles(base_url + 'page_' + str(num) + '.html')
