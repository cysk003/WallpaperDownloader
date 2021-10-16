import os
import requests
import shutil
import signal
import urllib.parse as parser
from requests.adapters import HTTPAdapter

from img_checker import check_resolution
from settings import Settings


class WallpaperDownloader():
    def __init__(self):
        self.__params__ = Settings('360_wallpaper.json')
        self.__base_url__ = self.__params__.get_setting('base_url')
        self.__save_path__ = self.__params__.get_setting('save_path')
        self.__ignore_year__ = self.__params__.get_setting('ignore_year')
        self.__session__ = requests.Session()
        self.__session__.mount('http://', HTTPAdapter(max_retries=3))
        self.__session__.mount('https://', HTTPAdapter(max_retries=3))
        self.__category__ = None
        self.__category_name = None
        self.__running__ = True

    def set_category(self, category, category_name):
        self.__category__ = category
        self.__category_name = category_name

    def set_save_path(self, save_path):
        self.__save_path__ = save_path
        self.__params__.set_setting('save_path', save_path)
        self.__params__.save_settings()

    def set_ignore_year(self, ignore_year):
        self.__ignore_year__ = ignore_year
        self.__params__.set_setting('ignore_year', int(ignore_year))
        self.__params__.save_settings()

    def get_categories(self):
        params = {
            'c': 'WallPaper',
            'a': 'getAllCategoriesV2',
            'from': ''
        }
        return self.__session__.get(self.__base_url__, params=params).json()['data']

    def get_apps_by_tags_from_category(self, catagory, tags, start=0, count=100):
        params = {
            'c': 'WallPaper',
            'a': 'getAppsByTagsFromCategory',
            'cids': int(catagory),
            'start': start,
            'count': count,
            'tags': parser.quote(tags)
        }
        try:
            response = self.__session__.get(
                self.__base_url__, params=params, timeout=10).json()
            total = int(response['total'])
            return {
                'total': total,
                'data': response['data']
            }
        except Exception as e:
            print(repr(e))
            return None

    def get_apps_by_category(self, catagory, start=0, count=100):
        params = {
            'c': 'WallPaper',
            'a': 'getAppsByCategory',
            'cid': int(catagory),
            'start': start,
            'count': count
        }
        try:
            response = self.__session__.get(
                self.__base_url__, params=params, timeout=10).json()
            total = int(response['total'])
            return {
                'total': total,
                'data': response['data']
            }
        except Exception as e:
            print(repr(e))
            return None

    def get_url_content(self, url, timeout):
        try:
            return self.__session__.get(url, timeout=timeout).content
        except Exception as e:
            print(repr(e))
            return None

    def stop(self):
        self.__running__ = False

    def run(self):
        start = 0
        page_size = 10
        if not os.path.exists(self.__save_path__):
            os.makedirs(self.__save_path__)
        response = self.get_apps_by_category(
            self.__category__, start, page_size)
        total = response['total']
        while response is not None and start <= total and self.__running__:
            for pic in response['data']:
                if self.__running__:
                    resolution = pic['resolution']
                    create_time: str = pic['create_time']
                    if create_time < str(self.__ignore_year__) or resolution < '1920x1080':
                        continue
                    pic_id = pic['id']
                    create_year = create_time.split('-')[0]
                    pic_save_path = os.path.join(self.__save_path__, self.__category_name, create_year)
                    if not os.path.exists(pic_save_path):
                        os.makedirs(pic_save_path)
                    path = os.path.join(pic_save_path, str(pic_id) + '_' +
                                        create_time.split(' ')[0].replace('-', '_') + '.jpg')
                    if os.path.exists(path):
                        print('[' + path + ']已存在')
                        continue
                    url_mid = pic['url_mid']
                    content_mid = self.get_url_content(url_mid, timeout=10)
                    url = pic['url']
                    content = self.get_url_content(url, timeout=10)
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
                        print('图片[' + pic_id + ']过小')
                        continue
                    if real_content:
                        with open(path, 'wb+') as f:
                            f.write(real_content)
                            f.close()
                        print('已下载[' + pic_id + ']至' + path)
                    else:
                        print('获取[' + pic_id + ']失败')
                else:
                    print('正在停止下载')
            start += page_size
            response = self.get_apps_by_category(
                self.__category__, start, page_size)


def main():
    downloader = WallpaperDownloader()
    running = True

    def stop(signum, frame):
        global running
        running = False
        downloader.stop()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    if running:
        cats = downloader.get_categories()
        num = 1
        for cat in cats:
            print('({}) {}'.format(num, cat['name']))
            num += 1
        order_str = input('输入序号并回车以下载, 输入"0"以退出:')
        try:
            order = int(order_str) - 1
        except Exception as e:
            print('无效数字: {}, 请重新运行本程序!'.format(order_str))
            exit(1)
        if order <= -1:
            exit(0)
        name = cats[order]['name']
        id = cats[order]['id']
        print('您选择了{}, ID={}:'.format(name, id))
        downloader.set_category(id, name)
        downloader.run()


if __name__ == '__main__':
    main()
