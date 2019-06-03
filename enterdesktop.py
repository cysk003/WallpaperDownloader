"""回车壁纸下载"""
from bs4 import BeautifulSoup
import os
import requests
from requests.adapters import HTTPAdapter
import logging
from settings import Settings
from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askdirectory

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def escape(input_str):
    char_arr = '?!=()#%&$^*|\\;\'\".,:\t\n\r\b'
    input_str = input_str.strip()
    for char in char_arr:
        input_str = input_str.replace(char, '_')
    return input_str


class EnterDesktop:
    def __init__(self):
        self.logger = logging.getLogger("EnterDesktop")
        self.__settings__ = Settings('enterdesktop.json')
        self.__session__ = requests.Session()
        self.__session__.mount('http://', HTTPAdapter(max_retries=2))
        self.__session__.mount('https://', HTTPAdapter(max_retries=2))
        self.__base_url__ = self.__settings__.get_setting('base_url')
        self.__save_path__ = self.__settings__.get_setting('save_path')
        self.__ignore_title__ = self.__settings__.get_setting('ignore_title')

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
            content = self.__session__.get(url, headers=headers, timeout=3).content
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
        base_pic_url = self.__base_url__ + '/' + pic_type + '/'
        num = 1
        while True:
            pic_url = base_pic_url + str(num) + '.html'
            soup = self.__parse_html__(pic_url)
            if soup:
                self.logger.info('开始下载:' + pic_type + ',第[' + str(num) + ']页')
                collections = self.__get_collections__(soup)
                if collections:
                    for collection in collections:
                        title = escape(collection['title'])
                        self.logger.info('开始下载:' + title)
                        href = collection['href']
                        soup = self.__parse_html__(href)
                        for pic in self.__get_pics_from_collection__(soup):
                            if not self.__ignore_title__:
                                path = os.path.join(self.__save_path__, title)
                                if not os.path.exists(path):
                                    os.makedirs(path)
                                pic_path = os.path.join(path, pic['name'])
                            else:
                                path = self.__save_path__
                                if not os.path.exists(path):
                                    os.makedirs(path)
                                pic_path = os.path.join(
                                    path, pic_type + '_' + title + '_' + pic['name'])
                            self.__download__(pic_path, pic['src'], href)
                else:
                    self.logger.warning('第[' + str(num) + ']页为空，跳出循环')
                    break
            else:
                self.logger.warning('在获取' + pic_url + '时出错，跳出循环')
                break
            num += 1

    def download_tuku(self, pic_type):
        base_pic_url = self.__base_url__ + '/' + pic_type + '/'
        num = 1
        while True:
            pic_url = base_pic_url + str(num) + '.html'
            soup = self.__parse_html__(pic_url)
            if soup:
                self.logger.info('开始下载:' + pic_type + ',第[' + str(num) + ']页')
                dds = soup.find_all('dd')
                if dds:
                    for dd in dds:
                        img = dd.find_all('img')[0]
                        img_href = img['src'].replace(
                            'edpic_360_360', 'edpic_source')
                        img_title = img['title'] + img_href.split('/')[-1]
                        parent_path = os.path.join(self.__save_path__, pic_type)
                        if not os.path.exists(parent_path):
                            os.makedirs(parent_path)
                        self.__download__(os.path.join(
                            parent_path, img_title), img_href, pic_url)
                else:
                    return []
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

    def start(self, tp='wallpaper'):
        if tp == 'wallpaper':
            self.__base_url__ = 'https://mm.enterdesk.com'
            types = self.__settings__.get_setting('types')
            for pic_type in types:
                self.logger.info("开始下载:" + pic_type)
                self.download_pictures(types[pic_type])
        else:
            self.__base_url__ = 'https://tu.enterdesk.com'
            self.logger.info("开始下载:图库")
            self.download_tuku('meinv')


class EnterDesktopUi:
    def __init__(self):
        self.__downloader__ = EnterDesktop()
        self.root = Tk()
        self.root.geometry('250x200')
        self.root.title('回车壁纸下载器 --by Zodiac')
        self.__categories_list__ = self.__downloader__.__settings__.get_setting('types')
        self.__category__ = None

    def get_categories(self):
        def get_selected(event):
            w = event.widget
            selected = w.get()
            self.__category__ = self.__categories_list__[selected]

        frame = Frame(self.root, width=250, height=50)
        categories_label = Label(frame, text='选择分类:')
        categories_label.pack(side=LEFT)
        options = []
        for c in self.__categories_list__:
            options.append(c)
        combobox = Combobox(frame)
        combobox['value'] = options
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

    def set_ignore_path(self):
        def get_selected(event):
            w = event.widget
            selected = w.get()
            if selected == '是':
                ignore_title = True
            else:
                ignore_title = False
            self.__downloader__.set_ignore_title(ignore_title)

        combobox = Combobox(self.root)
        categories_label = Label(self.root, text='是否为每个图集设置一个目录:')
        categories_label.pack(side=LEFT)
        options = ['是', '否']
        combobox['value'] = options
        combobox.current(1)
        combobox.bind('<<ComboboxSelected>>', get_selected)
        combobox.pack(side=RIGHT, after=categories_label)

    def start(self):
        tip_label = Label(self.root, text='点击开始下载后，请耐心等待~')
        tip_label.pack(side=BOTTOM)
        start_btn = Button(self.root, text='开始下载',
                           command=lambda: self.__downloader__.download_pictures(self.__category__))
        start_btn.pack(side=BOTTOM)
        self.get_categories()
        self.set_save_path()
        self.set_ignore_path()
        self.root.mainloop()


if __name__ == '__main__':
    ui = EnterDesktopUi()
    ui.start()
