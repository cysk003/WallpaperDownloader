"""美图录"""
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.meitulu.com/'
# guochan
# gangtai
# rihan
# xihuan
url_category = base_url + 'guochan/'
save_path = 'D:\\图片\\美图录'


def download_collections(url):
    html = str(session.get(url, timeout=3).content, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    collections = soup.find_all('div', class_=['boxs'])[
        0].find_all('ul', class_=['img'])[0].find_all('li')
    for c in collections:
        reffer = c.find_all('a')[0]['href']
        headers = {'Referer': reffer}
        pic_num = int(c.find_all('p', class_=False)[0].text.split(' ')[1])
        pic = c.find_all('img')[0]
        pic_url = pic['src']
        prefix = pic_url[0:pic_url.rfind('/')]
        pic_name = pic['alt'].strip().replace('<', '《').replace('>', '》') \
            .replace(':', '：')
        path = os.path.join(save_path, pic_name)
        if not os.path.exists(path):
            os.makedirs(path)
        for n in range(1, pic_num + 1):
            pic_save_path = os.path.join(path, str(n) + '.jpg')
            if os.path.exists(pic_save_path):
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


def get_total_collections(url):
    html = str(session.get(url, timeout=3).content, encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    pages = int(soup.find_all(id='pages')[0].find_all('a')[-2].text)
    return pages


if __name__ == "__main__":
    for num in range(1, get_total_collections(url_category) + 1):
        url = url_category + str(num) + '.html' if num != 1 else url_category
        download_collections(url)
    pass
