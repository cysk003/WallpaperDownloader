"""美图录"""
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path
import savepath
from multiprocessing import Pool, cpu_count
import sys
sys.setrecursionlimit(100000)

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.meitulu.com/'
dir_name = '美图录'
save_path = save_path = os.path.join(savepath.save_path, dir_name)


def escape(input_str):
    char_arr = '?!=()#%&$^*|\\;\'\".,:\t\n\r\b'
    input_str = input_str.strip()
    for char in char_arr:
        input_str = input_str.replace(char, '')
    return input_str


def download_collection(c):
    reffer = c.find_all('a')[0]['href']
    headers = {'Referer': reffer}
    pic_num = int(c.find_all('p', class_=False)[0].text.split(' ')[1])
    pic = c.find_all('img')[0]
    pic_url = pic['src']
    prefix = pic_url[0:pic_url.rfind('/')]
    pic_name = pic['alt'].strip().replace('<', '《').replace('>', '》') \
        .replace(':', '：').replace(' ', '')
    path = os.path.join(save_path, escape(pic_name.strip()))
    if not os.path.exists(path):
        os.makedirs(path)
    for n in range(1, pic_num + 1):
        pic_save_path = os.path.join(path, str(n) + '.jpg')
        if os.path.exists(pic_save_path) or savepath.check_exists(dir_name, escape(pic_name.strip()), str(n) + '.jpg'):
            print('[' + pic_save_path + ']已存在')
            continue
        content = None
        try:
            content = session.get(prefix+'/'+str(n) +
                                  '.jpg', timeout=3, headers=headers).content
        except Exception as e:
            print(repr(e))
            continue
        if content:
            with open(pic_save_path, 'wb') as f:
                f.write(content)
                f.close()
                print('已下载[' + pic_save_path + ']')


def download_collections(url):
    html = str(session.get(url, timeout=3).content, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    collections = soup.find_all('div', class_=['boxs'])[
        0].find_all('ul', class_=['img'])[0].find_all('li')
    pool = Pool(cpu_count() * 2)
    pool.map(download_collection, collections)
    pool.close()
    pool.join()


def get_total_collections(url):
    html = str(session.get(url, timeout=3).content, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    pages = int(soup.find_all(id='pages')[0].find_all('a')[-2].text)
    return pages


if __name__ == "__main__":
    for cat in ['guochan', 'gangtai', 'rihan', 'xihuan']:
        url_category = base_url + cat + '/'
        for num in range(1, get_total_collections(url_category) + 1):
            url = url_category + str(num) + \
                '.html' if num != 1 else url_category
            download_collections(url)
        pass
