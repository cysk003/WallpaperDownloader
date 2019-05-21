"""mm131"""
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

base_url = 'http://www.mm131.com/'
url_category = base_url + 'qipao/' #xinggan qingchun xiaohua chemo qipao
save_path = 'D:\\图片\\mm131'


def get_link(x):
    return x.find_all('a')[0]['href'], x.find_all('img')[0]['alt']


def get_collection_list(url):
    content = str(session.get(url,
                              timeout=3).content, encoding='gbk')
    soup = BeautifulSoup(content, 'html.parser')
    dl = soup.find_all('dl', class_='list-left public-box')[0]
    dds = map(get_link, dl.find_all('dd', class_=False))
    next_page = dl.find_all('dd', class_=['page'])[0].find_all('a', string='下一页')
    prefix = url[0:url.rfind('/')]
    next_page_url = prefix + '/' + next_page[0]['href'] if next_page else None
    return dds, next_page_url


def get_img(url: str):
    content = str(session.get(url,
                              timeout=3).content, encoding='gbk')
    soup = BeautifulSoup(content, 'html.parser')
    pic = soup.find_all('div', class_=['content-pic'])[0].find_all('img')[0]
    pic_url = pic['src']
    pic_name = pic['alt']
    pic_next = soup.find_all(
        'div', class_=['content-page'])[0].find_all('a', string='下一页')
    prefix = url[0:url.rfind('/')]
    pic_next_url = prefix + '/' + pic_next[0]['href'] if pic_next else None
    return pic_url, pic_name, pic_next_url


if __name__ == "__main__":
    page = get_collection_list(url_category)
    while page[1]:
        lst = page[0]
        next_page = page[1]
        print("NextPage:" + next_page)
        for u in lst:
            title = u[1]
            path = os.path.join(save_path, title)
            if not os.path.exists(path):
                os.makedirs(path)
            img = get_img(u[0])
            headers = {'Referer': u[0]}
            while img[2]:
                img_name = img[1] + '.jpg'
                img_next_url = img[2]
                img_path = os.path.join(path, img_name)
                if os.path.exists(img_path):
                    print('[' + img_path + ']已存在')
                    img = get_img(img_next_url)
                    continue
                img_src = img[0]
                img_content = None  
                try:
                    img_content = session.get(img_src, timeout=3, headers=headers).content
                except Exception as e:
                    print(repr(e))
                    continue
                with open(img_path, 'wb') as f:
                    f.write(img_content)
                    f.close()
                    print('已下载[' + img_name + ']至' + path)
                img = get_img(img_next_url)
            else:
                img_name = img[1] + '.jpg'
                img_path = os.path.join(path, img_name)
                if os.path.exists(img_path):
                    print('[' + img_path + ']已存在')
                    continue
                img_src = img[0]
                img_content = session.get(img_src, timeout=3, headers=headers).content
                with open(img_path, 'wb') as f:
                    f.write(img_content)
                    f.close()
                    print('已下载[' + img_name + ']至' + path)
        page = get_collection_list(next_page)
    else:
        lst = page[0]
        for u in lst:
            title = u[1]
            path = os.path.join(save_path, title)
            if not os.path.exists(path):
                os.makedirs(path)
            img = get_img(u[0])
            headers = {'Referer': u[0]}
            while img[2]:
                img_name = img[1] + '.jpg'
                img_next_url = img[2]
                img_path = os.path.join(path, img_name)
                if os.path.exists(img_path):
                    print('[' + img_path + ']已存在')
                    img = get_img(img_next_url)
                    continue
                img_src = img[0]
                img_content = session.get(img_src, timeout=3, headers=headers).content
                with open(img_path, 'wb') as f:
                    f.write(img_content)
                    f.close()
                    print('已下载[' + img_name + ']至' + path)
                img = get_img(img_next_url)
            else:
                img_name = img[1] + '.jpg'
                img_path = os.path.join(path, img_name)
                if os.path.exists(img_path):
                    print('[' + img_path + ']已存在')
                    continue
                img_src = img[0]
                img_content = None  
                try:
                    img_content = session.get(img_src, timeout=3, headers=headers).content
                except Exception as e:
                    print(repr(e))
                    continue
                with open(img_path, 'wb') as f:
                    f.write(img_content)
                    f.close()
                    print('已下载[' + img_name + ']至' + path)
