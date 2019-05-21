import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.mzitu.com'
all_url = base_url + '/all'
old_url = base_url + '/old'
save_path = 'D:\\图片\\妹子图'

if not os.path.exists(save_path):
    os.makedirs(save_path)

cookies = None


def parse_url(url, headers=None, timeout=5, cookies=None):
    response = session.get(url, headers=headers,
                           timeout=timeout, cookies=cookies)
    if response.status_code == 200:
        cookies = response.cookies
        content = response.content
        encoding = response.encoding
        content_str = str(content, encoding=encoding)
        if content_str:
            return BeautifulSoup(content_str, 'html.parser')
        else:
            return None
    else:
        return None


def get_catagories():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
    }
    uls = parse_url(all_url, headers=headers, cookies=cookies).find_all('ul', class_='archives') + \
        parse_url(old_url, headers=headers, cookies=cookies).find_all(
            'ul', class_='archives')
    a_links = [ul.find_all('a', target='_blank') for ul in uls]
    links = []
    for x in a_links:
        for y in x:
            links.append(y['href'])
    return links


def format(i):
    if i < 10:
        return '0' + str(i)
    else:
        return str(i)


def get_pics(href):
    index = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Connection': 'keep-alive',
        'Referer': href
    }
    content = parse_url(href, headers=headers, cookies=cookies)
    div = content.find('div', class_='main-image') if content else None
    if div:
        pic = div.find('img')
        pic_base_url = pic['src'][:-6]
        pic_title = pic['alt']
        path = os.path.join(save_path, pic_title)
        if not os.path.exists(path):
            os.makedirs(path)
        while True:
            pac_save_path = os.path.join(path, str(index) + '.jpg')
            if os.path.exists(pac_save_path):
                index += 1
                continue
            else:
                pic_url = pic_base_url + format(index) + '.jpg'
                get_pic_response = session.get(
                    pic_url, headers=headers, cookies=cookies, timeout=5)
                if get_pic_response and get_pic_response.status_code == 200:
                    with open(pac_save_path, 'wb+') as f:
                        f.write(get_pic_response.content)
                else:
                    break
                index += 1


catas = get_catagories()
for cat in catas:
    get_pics(cat)
