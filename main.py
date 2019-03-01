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
    return session.get(base_url, params=params).json()['data']


if __name__ == "__main__":
    # catagories = get_catagories()['data']
    # for data in catagories:
        # data['name']
    pics = get_apps_by_tags_from_category(6, '清纯', 0, 10)
    for pic in pics:
        print(pic)
    pass
