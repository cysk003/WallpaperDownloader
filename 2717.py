"""2717"""
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path
import savepath

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'https://www.2717.com'
pic_url = base_url + '/ent/meinvtupian/'
save_path = os.path.join(savepath.save_path, '2717')

start_page = 1
while True:
    url = pic_url + 'list_11_' + str(start_page) + '.html'
    content = None
    try:
        content = session.get(url, timeout=3).content
    except Exception as e:
        print(repr(e))
    if not content:
        break
    html = str(content, encoding='gbk')
    soup = BeautifulSoup(html, 'html.parser')
    collections = soup.select('.MeinvTuPianBox')[0]
    for x in collections.find_all('li'):
        collection = x.find_all('a', class_='MMPic')[0]
        href = collection['href']
        real_href = base_url + href
        href_base = real_href[0: real_href.rfind('.')]
        title = collection['title']
        if not os.path.exists(os.path.join(save_path, title)):
            os.makedirs(os.path.join(save_path, title))
        href_num = 1
        content2 = None
        try:
            content2 = session.get(href_base + '_' + str(href_num) + '.html', timeout=3).content
        except Exception as e:
            print(repr(e))
            continue
        html2 = str(content2, encoding='gbk')
        soup2 = BeautifulSoup(html2, 'html.parser')
        while soup2:
            img = None
            try:
                img = soup2.find_all('div', id='picBody')[0].find_all('img')[0]
            except Exception as e:
                print(repr(e))
                break
            img_url = img['src']
            img_name = img_url[img_url.rfind('/') + 1:]
            img_save_path = os.path.join(save_path, title, img_name)
            if os.path.exists(img_save_path):
                print(img_save_path + '已存在')
                href_num += 1
                try:
                    soup2 = BeautifulSoup(str(session.get(href_base + '_' + str(href_num) + '.html', timeout=3).content, 'gbk'),'html.parser')
                except Exception as e:
                    print(repr(e))
                    continue
                continue
            try:
                c = session.get(img_url, timeout=3).content
            except Exception as e:
                print(repr(e))
                continue
            with open(img_save_path, 'wb') as f:
                f.write(c)
                f.close()
                print(img_save_path + '已下载')
            href_num += 1
            content2 = None
            try:
                soup2 = BeautifulSoup(
                    str(session.get(href_base + '_' + str(href_num) + '.html', timeout=3).content, 'gbk'),
                    'html.parser')
            except Exception as e:
                print(repr(e))
                continue
    start_page += 1
