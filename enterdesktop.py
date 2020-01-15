"""回车壁纸下载"""
from bs4 import BeautifulSoup
import os
import requests
from requests.adapters import HTTPAdapter
import logging
import signal
from settings import Settings
from multiprocessing import Pool, cpu_count
from img_checker import check_resolution

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def escape(input_str):
    char_arr = '?!=()#%&$^*|\\;\'\".,:\t\n\r\b'
    input_str = input_str.strip()
    for char in char_arr:
        input_str = input_str.replace(char, '_')
    return input_str


class EnterDesktop():
    def __init__(self):
        self.logger = logging.getLogger("EnterDesktop")
        self.__settings__ = Settings('enterdesktop.json')
        self.__session__ = requests.Session()
        self.__session__.mount('http://', HTTPAdapter(max_retries=2))
        self.__session__.mount('https://', HTTPAdapter(max_retries=2))
        self.__base_url__ = self.__settings__.get_setting('base_url')
        self.__save_path__ = self.__settings__.get_setting('save_path')
        self.__ignore_title__ = self.__settings__.get_setting('ignore_title')
        self.__working__ = True
        self.__pic_type__ = None

    def stop(self):
        self.__working__ = False

    def set_pic_type(self, pic_type):
        self.__pic_type__ = pic_type

    def set_save_path(self, save_path):
        self.__save_path__ = save_path
        self.__settings__.set_setting('save_path', save_path)
        self.__settings__.save_settings()

    def set_ignore_title(self, ignore_title):
        self.__ignore_title__ = ignore_title
        self.__settings__.set_setting('ignore_title', ignore_title)
        self.__settings__.save_settings()

    def __get_url_content__(self, url, headers=None):
        try:
            content = self.__session__.get(
                url, headers=headers, timeout=3).content
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

    def __download_pics__(self, collection):
        if self.__working__:
            title = escape(collection['title'])
            self.logger.info('开始下载:' + title)
            href = collection['href']
            soup = self.__parse_html__(href)
            for pic in self.__get_pics_from_collection__(soup):
                if self.__working__:
                    if self.__ignore_title__ is False:
                        path = os.path.join(
                            self.__save_path__, self.__pic_type__, title)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        pic_path = os.path.join(
                            path, pic['name'])
                    else:
                        if not os.path.exists(self.__save_path__):
                            os.makedirs(self.__save_path__)
                        pic_path = os.path.join(self.__save_path__, pic['name'])
                    self.__download__(pic_path, pic['src'], href)
                else:
                    print('正在停止下载图片')
        else:
            print('正在停止下载合集')

    def __download__(self, path, src, referer):
        if os.path.exists(path):
            self.logger.info('[' + path + ']已存在')
            return
        else:
            content = self.__get_url_content__(src, {'Referer': referer})
            if content:
                if check_resolution(content, 1920, 1080):
                    with open(path, 'wb') as f:
                        f.write(content)
                        self.logger.info('下载:[' + src + ']到[' + path + ']')
                else:
                    self.logger.warn('{}分辨率小于1920x1080'.format(src))

    def run(self, use_multi_processor=True):
        base_pic_url = self.__base_url__ + '/' + self.__pic_type__ + '/'
        num = 1
        while self.__working__:
            pic_url = base_pic_url + str(num) + '.html'
            soup = self.__parse_html__(pic_url)
            if soup:
                self.logger.info('开始下载:' + self.__pic_type__ +
                                 ',第[' + str(num) + ']页')
                collections = self.__get_collections__(soup)
                if collections:
                    if use_multi_processor:
                        pool = Pool(cpu_count() * 2)
                        result = pool.map(self.__download_pics__, collections)
                        pool.close()
                        pool.join()
                    else:
                        for collection in collections:
                            self.__download_pics__(collection)
                else:
                    self.logger.warning('第[' + str(num) + ']页为空，跳出循环')
                    break
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
            return [{'title': dd.find_all('img')[0]['title'].strip(), 'href': dd.find_all('a')[0]['href']} for dd in
                    dds]
        else:
            return []

    def __parse_html__(self, url):
        text = self.__get_url_text__(url, encoding='utf-8')
        if not text:
            return None
        else:
            return BeautifulSoup(text, 'html.parser')


def main():
    ed = EnterDesktop()
    running = True
    def stop(signum, frame):
        global running
        running = False
        ed.stop()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    types = ed.__settings__.get_setting('types')
    for tp in types:
        if running:
            pic_type = types[tp]
            ed.set_pic_type(pic_type)
            ed.run(False)


if __name__ == '__main__':
    main()
