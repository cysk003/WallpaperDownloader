"""回车壁纸下载"""
from bs4 import BeautifulSoup
import os
from multiprocessing.pool import ThreadPool
import requests
from requests.adapters import HTTPAdapter
import logging

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class EnterDesktop:
    def __init__(self, save_path=None):
        self.logger = logging.getLogger("EnterDesktop")
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.base_url = 'https://mm.enterdesk.com'
        self.save_path = 'D:\\回车壁纸'
        self.pool = ThreadPool(4)

    def __get_url_content__(self, url):
        try:
            content = self.session.get(url, timeout=3).content
            return content
        except Exception as e:
            self.logger.warning(repr(e))
            return None

    def __get_url_text__(self, url, encoding):
        content = self.__get_url_content__(url)
        if not content:
            return None
        else:
            return str(content, encoding=encoding)

    def __download__(self, path, src):
        if os.path.exists(path):
            return
        else:
            content = self.__get_url_content__(src)
            if content:
                with open(path, 'wb') as f:
                    f.write(content)
                    print('下载:[' + src + ']到[' + path + ']')

    def download_pictures(self, pic_type):
        base_pic_url = self.base_url + '/' + pic_type + '/'
        num = 1
        while True:
            pic_url = base_pic_url + str(num) + '.html'
            soup = self.__parse_html__(pic_url)
            if soup:
                collections = self.__get_collections__(soup)
                if collections:
                    for collection in collections:
                        title = collection['title']
                        href = collection['href']
                        soup = self.__parse_html__(href)
                        for pic in self.__get_pics_from_collection__(soup):
                            path = os.path.join(self.save_path, title)
                            if not os.path.exists(path):
                                os.makedirs(path)
                            self.__download__(os.path.join(
                                path, pic['name']), pic['src'])
            else:
                break
            num += 1

    def __get_pics_from_collection__(self, soup):
        if soup:
            div = soup.find_all('div', class_='swiper-wrapper')[0]
            return [{'name': a['src'].split('/')[-1], 'src': a['src'].replace('edpic', 'edpic_source')} for a in div.find_all('a')]
        else:
            return []

    def __get_collections__(self, soup):
        dds = soup.find_all('dd')
        if dds:
            return [{'title': dd.find_all('img')[0]['title'], 'href': dd.find_all('a')[0]['href']} for dd in dds]
        else:
            return []

    def __parse_html__(self, url):
        text = self.__get_url_text__(url, encoding='utf-8')
        if not text:
            return None
        else:
            return BeautifulSoup(text, 'html.parser')

    def start(self):
        arr = [PicType.DALU, PicType.RIHAN, PicType.QINGCHUN, PicType.KEAI]
        for pic_type in arr:
            print("开始下载:" + pic_type)
            self.download_pictures(pic_type)


class PicType():
    DALU = 'dalumeinv'
    RIHAN = 'rihanmeinv'
    QINGCHUN = 'qingchunmeinv'
    KEAI = 'keaimeinv'


EnterDesktop = EnterDesktop()
EnterDesktop.start()
