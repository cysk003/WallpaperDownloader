"""亿秀网"""
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'http://www.tu11.com'
save_path = 'D:\\图片\\亿秀'


def get_collections(collection_url):
    res = []
    try:
        html = str(session.get(collection_url, timeout=3).content, 'gbk')
        soup = BeautifulSoup(html, 'html.parser')
        lis = soup.find_all('li', class_=['col-xs-1-5'])
        for li in lis:
            collection = li.find_all('a')[0]
            href = base_url + collection['href']
            title = collection.find_all('img')[0]['alt']
            res.append((title, href))
        return res
    except Exception as e:
        print(repr(e))
        return None


def get_img_start_url(url):
    try:
        html = str(session.get(url, timeout=3).content, 'gbk')
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find_all('div', class_='nry')[0]
        img = div.find_all('img')[0]
        img_url2 = img['src']
        return img_url2[0: img_url2.rfind('/')]
    except Exception as e:
        print(repr(e))
        return None


def download(url, path, headers=None):
    if os.path.exists(path):
        print(path + '已存在')
        return True
    content = None
    try:
        response = session.get(url, timeout=3, headers=headers)
        state = response.status_code
        if state != 200:
            return False
        content = response.content
    except Exception as e:
        print(repr(e))
    if content:
        with open(path, 'wb') as f:
            f.write(content)
            f.close()
            print('已下载[' + url + ']至[' + path + ']')
        return True
    else:
        return False


sub_url_1 = '/qingchunmeinvxiezhen/list_4_'

num1 = 1
while True:
    collection_url = base_url + sub_url_1 + str(num1) + '.html'
    collections = get_collections(collection_url)
    if not collections:
        break
    for collection in collections:
        title = collection[0]
        p = os.path.join(save_path, title)
        if not os.path.exists(p):
            os.makedirs(p)
        href = collection[1]
        headers = {
            'Referer': href
        }
        img_url = get_img_start_url(href)
        num2 = 1
        while True:
            get_pic_res = download(img_url + '/' + str(num2) + '.jpg', os.path.join(save_path, title, str(num2) + '.jpg'),
                                   headers)
            if not get_pic_res:
                break
            num2 += 1
    num1 += 1