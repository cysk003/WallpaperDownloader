"""绝色美女网"""
import os.path
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

import savepath

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'http://www.jsmeinv.com'
save_path = save_path = os.path.join(savepath.save_path, '绝色美女')


def __get__(url_, headers_, encoding_):
    try:
        response = session.get(url_, headers=headers_, timeout=3)
        if response.status_code == 200:
            content = response.content
            if encoding_:
                return str(content, encoding_)
            else:
                return content
        else:
            return None
    except Exception as e:
        print(repr(e))
        return None


def get_collections(list_url):
    html = __get__(list_url, headers_=None, encoding_='gbk')
    if not html:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    collection_list = [li.find_all('a')[0] for li in soup.find_all('div', id='list')[0].find_all('li')]
    return [(base_url + a['href'], a['title']) for a in collection_list]


def download(content, path):
    if content:
        with open(path, 'wb') as f:
            f.write(content)
            f.close()
            print('已下载至[' + path + ']')
            return True
    else:
        return False


def escape(input_str):
    esp = """/\\:*"<>|?"""
    for x in esp:
        input_str = input_str.replace(x, '')
    return input_str


def get_pic(pic_url, title):
    html = __get__(url_=pic_url, headers_=None, encoding_='gbk')
    if not html:
        return False
    path = os.path.join(save_path, escape(title))
    if not os.path.exists(path):
        os.makedirs(path)
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', id='picg')
    if not divs:
        return False
    pic = divs[0].find_all('img')[0]
    pic_src = pic['src']
    pic_name = pic_src[pic_src.rfind('/') + 1:]
    pic_save_path = os.path.join(path, pic_name)
    if os.path.exists(pic_save_path):
        print(pic_save_path + '已存在')
        return True
    headers = {
        'Referer': pic_url
    }
    pic_content = __get__(pic_src, headers_=headers, encoding_=None)
    if not pic_content:
        return False
    return download(pic_content, pic_save_path)


# 1 性感美女
# 2 青春靓丽
# 5 街拍自拍
# 9 内衣丝袜
# 11 明星秀女
# 18 精品套图
# 24 高清套图
# 25 无圣光
sub_url = '/meinv/niebiao/25_'

num1 = 1
while True:
    list_url = base_url + sub_url + str(num1) + '.html'
    collection_list = get_collections(list_url)
    if not collection_list:
        break
    else:
        for collection in collection_list:
            print('开始下载 ' + collection[1])
            num2 = 1
            while True:
                if num2 != 1:
                    collection_href = collection[0]
                    collection_href_prefix = collection_href[0:collection_href.rfind('/')]
                    collection_href_suffix = collection_href[collection_href.rfind('/') + 1:]
                    collection_href_suffix_num = collection_href_suffix[0:collection_href_suffix.rfind('.')]
                    collection_href = collection_href_prefix + '/' + collection_href_suffix_num + '_' + str(
                        num2) + '.html'
                else:
                    collection_href = collection[0]
                if not get_pic(collection_href, collection[1]):
                    break
                num2 += 1
    num1 += 1
