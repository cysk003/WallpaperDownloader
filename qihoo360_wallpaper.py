import os
import urllib.parse as parser

import requests
from requests.adapters import HTTPAdapter
from settings_ import Settings
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory
from threading import Thread


class WallpaperDownloader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__params__ = Settings('360_wallpaper.json')
        self.__base_url__ = self.__params__.get_setting('base_url')
        self.__save_path__ = self.__params__.get_setting('save_path')
        self.__ignore_year__ = self.__params__.get_setting('ignore_year')
        self.__session__ = requests.Session()
        self.__session__.mount('http://', HTTPAdapter(max_retries=3))
        self.__session__.mount('https://', HTTPAdapter(max_retries=3))
        self.__category__ = None
        self.__running__=True

    def set_category(self, category):
        self.__category__ = category

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
        return self.__session__.get(self.__base_url__, params=params).json()

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
        self.__running__=False

    def run(self):
        start = 0
        page_size = 10
        if not os.path.exists(self.__save_path__):
            os.makedirs(self.__save_path__)
        response = self.get_apps_by_category(self.__category__, start, page_size)
        total = response['total']
        while response is not None and start <= total and self.__running__:
            for pic in response['data']:
                if self.__running__:
                    create_time: str = pic['create_time']
                    if create_time < str(self.__ignore_year__):
                        continue
                    pic_id = pic['id']
                    path = os.path.join(self.__save_path__, str(pic_id) + '_' +
                                        create_time.split(' ')[0].replace('-', '_') + '.jpg')
                    if os.path.exists(path):
                        print('[' + path + '已存在')
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
            response = self.get_apps_by_category(self.__category__, start, page_size)


class WallpaperDownloaderUi:
    def __init__(self):
        self.__downloader__ = WallpaperDownloader()
        self.root = Tk()
        self.root.geometry('250x250')
        self.root.title('360壁纸下载器 --by Zodiac')
        self.__categories_list__ = {}

    def get_categories(self):
        def get_selected(event):
            w = event.widget
            selected = w.get()
            self.__downloader__.set_category(self.__categories_list__[selected])

        frame = Frame(self.root, width=250, height=50)
        categories_label = Label(frame, text='选择分类:')
        categories_label.pack(side=LEFT)
        categories = self.__downloader__.get_categories()['data']
        self.__downloader__.set_category(categories[0]['id'])
        options = []
        for c in categories:
            self.__categories_list__[c['name']] = c['id']
            options.append(c['name'])
        combobox = Combobox(frame)
        combobox['value'] = options
        combobox.current(0)
        combobox.bind('<<ComboboxSelected>>', get_selected)
        combobox.pack(side=LEFT, after=categories_label)
        frame.pack_propagate(0)
        frame.pack(side=TOP)

    def set_save_path(self):
        frame = Frame(self.root, width=250, height=50)
        path_label = Label(frame, text=self.__downloader__.__save_path__)

        def get_selected_path():
            selected_path = askdirectory()
            self.__downloader__.set_save_path(selected_path)
            path_label['text'] = selected_path

        path_btn = Button(frame, text='选择下载文件夹:', command=get_selected_path)
        path_btn.pack(side=LEFT)
        path_label.pack(side=LEFT, after=path_btn)
        frame.pack_propagate(0)
        frame.pack(side=BOTTOM)

    def start(self):
        tip_label = Label(self.root, text='点击开始下载后，请耐心等待~')
        tip_label.pack(side=BOTTOM)
        start_btn = Button(self.root, text='开始下载',
                           command=self.__downloader__.start)
        start_btn.pack(side=BOTTOM)
        stop_btn = Button(self.root, text='停止下载',
                           command=self.__downloader__.stop)
        stop_btn.pack(side=BOTTOM, before=start_btn)
        self.get_categories()
        self.set_save_path()
        self.root.mainloop()


def main():
    downloader_ui = WallpaperDownloaderUi()
    downloader_ui.start()


if __name__ == '__main__':
    main()

