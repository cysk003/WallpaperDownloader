import io
import json
import os
import sys
import urllib.parse as parser
import math

import requests
from requests.adapters import HTTPAdapter

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
        response = session.get(base_url, params=params, timeout=10).json()
        total = int(response['total'])
        return {
            'total': total,
            'data': response['data']
        }
    except Exception as e:
        print(repr(e))
        return None


def get_apps_by_category(catagory, start=0, count=100):
    params = {
        'c': 'WallPaper',
        'a': 'getAppsByCategory',
        'cid': int(catagory),
        'start': start,
        'count': count
    }
    try:
        response = session.get(base_url, params=params, timeout=10).json()
        total = int(response['total'])
        return {
            'total': total,
            'data': response['data']
        }
    except Exception as e:
        print(repr(e))
        return None


def get_url_content(url, timeout):
    try:
        return session.get(url, timeout=timeout).content
    except Exception as e:
        print(repr(e))
        return None


if __name__ == "__main__":
    category = 6 # 美女
    start = 0
    page_size = 10
    p = os.path.join(save_path)
    if not os.path.exists(p):
        os.makedirs(p)
    response = get_apps_by_category(category, start, page_size)
    total = response['total']
    while response is not None and start <= total:
        for pic in response['data']:
            id = pic['id']
            path = os.path.join(p, str(id) + '.jpg')
            if os.path.exists(path):
                print('[' + path + '已存在')
                continue
            url_mid = pic['url_mid']
            content_mid = get_url_content(url_mid, timeout=10)
            url = pic['url']
            content = get_url_content(url, timeout=10)
            real_content = None
            if content_mid and content:
                if len(content_mid) > len(content):
                    real_content = content_mid
                else:
                    real_content = content
            elif content_mid and not content:
                real_content = content_mid
            else:
                real_content = content
            if real_content and len(real_content) <= 50 * 1024:
                print('图片[' + id + ']过小')
                continue
            if real_content:
                with open(path, 'wb+') as f:
                    f.write(real_content)
                    f.close()
                print('已下载[' + id + ']至' + path)
            else:
                print('获取[' + id + ']失败')
        start += page_size
        response = get_apps_by_category(category, start, page_size)
        print('start:' + str(start) + ', total:' + str(total))
    print('下载完成！')
