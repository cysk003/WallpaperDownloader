import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import os.path

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


base_url = 'https://www.walltu.com'
cat_url = base_url + '/mn'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
}


def escape(input_str):
    char_arr = '?!=()#%&$^*|\\;\'\".,:\t\n\r\b'
    input_str = input_str.strip()
    for char in char_arr:
        input_str = input_str.replace(char, '_')
    return input_str


def get_all_cats():
    response = session.get(cat_url, headers=headers, timeout=(3, 3))
    arr = []
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        all_cats = soup.find_all('p', id='q')
        for ele in all_cats:
            hrefs = ele.find_all('a')
            for href in hrefs:
                arr.append(
                    {'name': href.string, 'href': base_url + href['href']})
        return arr
    else:
        return None


def get_articles(ele):
    href = ele['href']
    response = session.get(href, headers=headers, timeout=(3, 3))
    if response.status_code == 200:
        content = str(response.content, 'utf-8')
        print(content)
    pass




cats = get_all_cats()
get_articles(cats[0])
