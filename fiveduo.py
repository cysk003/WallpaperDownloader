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


base_url = 'https://www.555duo.net'
dir_name = '555duo'
save_path = save_path = os.path.join(savepath.save_path, dir_name)

if not os.path.exists(save_path):
    os.makedirs(save_path)

headers = {
    'Referer': None,
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

cookies = None


def get_movie_list(index: int):
    global cookies
    res = []
    url: str = base_url + "/a/movie/list_1_{}.html".format(index)
    response = session.get(url, headers=headers,
                           cookies=cookies, timeout=(5, 5))
    if response.status_code == 200:
        cookies = response.cookies
        content = str(response.content, 'gb2312')
        soup = BeautifulSoup(content, 'html.parser')
        ul = soup.find('ul', class_='ul2')
        if ul:
            elements = ul.find_all('a')
            for element in elements:
                res.append(
                    {'title': element['title'], 'href': element['href']})
    return res


def get_move_href(href: str):
    global cookies
    response = session.get(href, headers=headers,
                           cookies=cookies, timeout=(5, 5))
    if response.status_code == 200:
        cookies = response.cookies
        content = str(response.content, 'gb2312')
        soup = BeautifulSoup(content, 'html.parser')
        downloads = soup.find_all('a', class_='down')
        if downloads:
            return downloads[-1]['href']
    return None


def download(path: str, href: str):
    global cookies
    response = session.get(href, headers=headers,
                           cookies=cookies, timeout=(30, 30))
    if response.status_code == 200:
        cookies = response.cookies
        with open(path, 'wb+') as f:
            f.write(response.content)
            print("Download {} to {}".format(href, path))


if __name__ == "__main__":
    # movies = get_movie_list(1)
    # print(movies)
    # get_move_href('https://www.555duo.net/a/html/11643.html')

    num: int = 1
    while True:
        print("Start download page {}".format(num))
        movies = get_movie_list(num)
        if movies:
            for movie in movies:
                print(movie)
                title = movie['title']
                href = movie['href']
                headers['Referer'] = href
                movie_href = get_move_href(href)
                print(movie_href)
                if movie_href:
                    _, suffix = os.path.splitext(movie_href.split('/')[-1])
                    p = os.path.join(save_path, title + suffix)
                    if os.path.exists(p):
                        print("{} already exists")
                    else:
                        download(p, movie_href)
        num += 1
