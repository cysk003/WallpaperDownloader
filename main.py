import os

import requests
from requests.adapters import HTTPAdapter
import json
import urllib.parse as parser

import params

save_path = params.save_path
base_url = params.base_url
tags = params.tags

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


def get_max_num_of_wallpapers(path):
    max = 1
    if not os.path.exists(path):
        os.makedirs(path)
        return max
    for pic_name in os.listdir(path):
        print(pic_name)
        pass

def get_categories():
    params = {
        'c': 'WallPaper',
        'a': 'getAllCategoriesV2',
        'from': ''
    }
    return session.get(base_url, params=params).json()


def get_apps_by_tags_from_category(catagory, tags, start=0, count=100):
    params = {
        'c': 'WallPaper',
        'a': 'getAppsByTagsFromCategory',
        'cids': int(catagory),
        'start': start,
        'count': count,
        'tags': parser.quote(tags)
    }
    try:
        return session.get(base_url, params=params).json()['data']
    except Exception as e:
        print(repr(e))
        return None

def get_url_content(url):
    return requests.get(url).content


if __name__ == "__main__":
    tags = '清纯'
    start = 0
    page_size = 50

    pics = get_apps_by_tags_from_category(6, tags, start, page_size)
    while pics is not None:
        for pic in pics:
            id = pic['id']
            url = pic['url']
            content = get_url_content(url)
            p = os.path.join(save_path, tags,)
            if not os.path.exists(p):
                os.makedirs(p)
            path = os.path.join(p, str(id) + '.jpg')
            with open(path, 'wb+') as f:
                f.write(content)
                f.close()
            print('已下载[' + id +']至' + path)
        start += page_size
        pics = get_apps_by_tags_from_category(6, tags, start, page_size)