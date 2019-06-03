import json
import os
import sys


class Settings:
    def __init__(self, path, default_settings={}):
        if not os.path.exists(path):
            print('Invalid path:' + path)
            sys.exit(1)
        self.__path__ = path
        self.__default_settings__ = default_settings
        loaded_settings = self.load_settings()
        for key in loaded_settings:
            self.__default_settings__[key] = loaded_settings[key]

    def load_settings(self):
        if os.path.exists(self.__path__):
            with open(self.__path__, 'rb+') as f:
                content = f.read()
                return json.loads(content, encoding='utf-8')
        else:
            return {}

    def save_settings(self):
        with open(self.__path__, 'wb+') as f:
            f.write(json.dumps(self.__default_settings__, indent=4, ensure_ascii=False).encode('utf-8'))

    def get_setting(self, key):
        if key in self.__default_settings__:
            return self.__default_settings__[key]
        else:
            return None

    def set_setting(self, key, value):
        self.__default_settings__[key] = value
