"""回车壁纸下载"""
from bs4 import BeautifulSoup
import os
from multiprocessing.pool import ThreadPool
import requests
from requests.adapters import HTTPAdapter
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class EnterDesktop:
    def __init__(self, save_path=None, ignore_title=False):
        self.logger = logging.getLogger("EnterDesktop")
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=2))
        self.session.mount('https://', HTTPAdapter(max_retries=2))
        self.base_url = 'https://mm.enterdesk.com'
        self.save_path = 'D:\\回车壁纸'
        self.ignore_title = ignore_title
        self.pool = ThreadPool(4)

    def __get_url_content__(self, url, headers=None):
        try:
            content = self.session.get(url, headers=headers, timeout=3).content
            return content
        except Exception as e:
            self.logger.warning('在获取:' + url + '时出错')
            self.logger.error(e)
            return None

    def __get_url_text__(self, url, encoding, headers=None):
        content = self.__get_url_content__(url, headers)
        if not content:
            return None
        else:
            try:
                return str(content, encoding=encoding)
            except Exception as e:
                self.logger.error(e)
                return None

    def __download__(self, path, src, referer):
        if os.path.exists(path):
            self.logger.info('[' + path + ']已存在')
            return
        else:
            content = self.__get_url_content__(src, {'Referer': referer})
            if content:
                with open(path, 'wb') as f:
                    f.write(content)
                    self.logger.info('下载:[' + src + ']到[' + path + ']')

    def download_pictures(self, pic_type):
        base_pic_url = self.base_url + '/' + pic_type + '/'
        num = 1
        while True:
            pic_url = base_pic_url + str(num) + '.html'
            soup = self.__parse_html__(pic_url)
            if soup:
                self.logger.info('开始下载:' + pic_type + ',第[' + str(num) + ']页')
                collections = self.__get_collections__(soup)
                if collections:
                    for collection in collections:
                        title = collection['title']
                        self.logger.info('开始下载:' + title)
                        href = collection['href']
                        soup = self.__parse_html__(href)
                        for pic in self.__get_pics_from_collection__(soup):
                            path = os.path.join(self.save_path, title) if not self.ignore_title else self.save_path
                            if not os.path.exists(path):
                                os.makedirs(path)
                            if not self.ignore_title:
                                pic_path = os.path.join(path, pic['name'])
                            else:
                                pic_path = os.path.join(path, title + '_' + pic['name'])
                            self.__download__(pic_path, pic['src'], href)
            else:
                self.logger.warning('在获取' + pic_url + '时出错，跳出循环')
                break
            num += 1

    def __get_pics_from_collection__(self, soup):
        if soup:
            div = soup.find_all('div', class_='swiper-wrapper')[0]
            return [{'name': a['src'].split('/')[-1], 'src': a['src'].replace('edpic', 'edpic_source')} for a in
                    div.find_all('a')]
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
            self.logger.info("开始下载:" + pic_type)
            self.download_pictures(pic_type)


class PicType:
    DALU = 'dalumeinv'
    RIHAN = 'rihanmeinv'
    QINGCHUN = 'qingchunmeinv'
    KEAI = 'keaimeinv'


if __name__ == '__main__':
    EnterDesktop = EnterDesktop(ignore_title=True)
    EnterDesktop.start()
