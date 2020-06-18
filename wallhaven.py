import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from os import path
import os
import urllib3
from img_checker import check_resolution

urllib3.disable_warnings()

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


base_url = 'https://wallhaven.cc/'
download_url = 'https://w.wallhaven.cc/full/{}/{}'
save_path = '/home/liu/Pictures'
dir_name = 'wallheaven'
save_dir = path.join(save_path, dir_name)
small_save_dir = path.join(save_path, dir_name, 'small')
if not path.exists(save_dir):
    os.makedirs(save_dir)
if not path.exists(small_save_dir):
    os.makedirs(small_save_dir)

save_path = save_path = os.path.join(save_path, dir_name)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip",
    "Referer": None,
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

response = session.get(base_url, headers=headers, timeout=(10, 10))
if response.status_code == 200:
    cookies = response.cookies


def parse_html(url, referer=None):
    headers['Referer'] = referer
    resp = session.get(url, headers=headers, timeout=(3, 3), cookies=cookies)
    if resp.status_code == 200:
        html = resp.text
        return BeautifulSoup(html, 'html.parser')
    return None


def get_pics(page):
    print('开始下载第{}页。'.format(page))
    num = 0
    url = base_url + \
        "search?categories=110&purity=100&topRange=1y&sorting=toplist-beta&order=desc&page={}".format(
            page)
    soup = parse_html(url, url)
    if soup:
        section = soup.find('section', class_='thumb-listing-page')
        if section:
            pics = section.findAll('figure')
            for pic in pics:
                num += 1
                pic_url = pic.find('img')['data-src']
                is_png = pic.find('span', class_='png')
                pic_name = pic_url.split('/')[-1]
                if is_png:
                    pic_name = pic_name.replace('jpg', 'png')
                pic_url = download_url.format(
                    pic_name[:2], 'wallhaven-' + pic_name)
                pic_save_path = path.join(save_dir, pic_name)
                small_pic_save_path = path.join(small_save_dir, pic_name)
                if path.exists(pic_save_path) or path.exists(small_pic_save_path):
                    continue
                else:
                    headers['Referer'] = base_url + \
                        'w' + '/' + pic_name.split('.')[0]
                    try:
                        resp = session.get(
                            pic_url, headers=headers, timeout=(10, 10))
                        if resp.status_code == 200:
                            content = resp.content
                            if not check_resolution(content, 1920, 1080):
                                pic_save_path = small_pic_save_path
                            with open(pic_save_path, 'wb+') as f:
                                f.write(resp.content)
                                f.flush()
                                f.close()
                                print('下载到[{}]'.format(pic_save_path))
                    except Exception as e:
                        print(repr(e))
                        if path.exists(pic_save_path):
                            os.remove(pic_save_path)
    return num


pg = 1
while(get_pics(pg) > 0):
    pg += 1
