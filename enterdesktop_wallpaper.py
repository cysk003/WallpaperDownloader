"""回车壁纸美女图片下载"""
from bs4 import BeautifulSoup
import os
import requests
from requests.adapters import HTTPAdapter
import logging
import signal
import json
from typing import List
from multiprocessing import Pool, cpu_count
from img_checker import check_resolution

base_url = "https://www.enterdesk.com"
save_path = "/home/liubodong/Pictures/EnterDeskWallpaper"

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=2))
session.mount('https://', HTTPAdapter(max_retries=2))


def get_all_types() -> dict:
    url = base_url + "/zhuomianbizhi"
    content = session.get(url, timeout=(3, 3)).text
    soup = BeautifulSoup(content, "html.parser")
    types = soup.select(".main > .list_sel_box > ul")[0]
    d = {}
    for t in types.find_all("a")[2:]:
        d[t.text] = base_url + t["href"]
    return d


def get_collections(href: str) -> List[str]:
    response = session.get(href, timeout=(3, 3))
    if response.status_code == 200:
        content = session.get(href, timeout=(3, 3)).text
        if content:
            soup = BeautifulSoup(content, "html.parser")
            if soup:
                hrefs = soup.select("dd > a")
                if hrefs:
                    return [a["href"] for a in hrefs]
    return []


def get_pictures(href: str) -> List[str]:
    response = session.get(href, timeout=(3, 3))
    if response.status_code == 200:
        content = session.get(href, timeout=(3, 3)).text
        if content:
            soup = BeautifulSoup(content, "html.parser")
            if soup:
                hrefs = soup.select(".swiper-wrapper a")
                if hrefs:
                    return [a['src'].replace('edpic', 'edpic_source') for a in hrefs]
    return []


def download(pic_type: str, href: str) -> None:
    name = href.split("/")[-1]
    pic_save_dir = os.path.join(save_path, pic_type, name[:2])
    if not os.path.exists(pic_save_dir):
        os.makedirs(pic_save_dir)
    pic_save_path = os.path.join(pic_save_dir, name)
    if os.path.exists(pic_save_path):
        print("{} already exists!".format(pic_save_path))
        return
    response = session.get(href, timeout=(5, 5))
    if response.status_code == 200:
        content = response.content
        if check_resolution(content, 1920, 1080):
            with open(pic_save_path, "wb") as f:
                f.write(content)
                print("save {} to {}".format(href, pic_save_path))


if __name__ == "__main__":
    types: dict = get_all_types()
    for type_name in types:
        type_href: str = types[type_name] + "{}.html"
        page: int = 1
        collections: List[str] = get_collections(type_href.format(page))
        while collections:
            for collection in collections:
                try:
                    pics = get_pictures(collection)
                    for pic in pics:
                        try:
                            download(type_name, pic)
                        except Exception as e:
                            print("Exception at download!")
                            print(repr(e))
                except Exception as e:
                    print("Exception at get pictures!")
                    print(repr(e))
            page += 1
            collections: List[str] = get_collections(type_href.format(page))
