from PIL import Image
from io import BytesIO
import os

def check_resolution(img_content, width, height):
    img = Image.open(BytesIO(img_content))
    _width, _height = img.size
    return _width >= width and _height >= height


def check_file_resolution(file_path, width, height):
    img = Image.open(file_path)
    _width, _height = img.size
    return _width >= width and _height >= height

def remove_low_resolution_imgs(path, width, height):
    for pic in os.listdir(path):
        pic_path = os.path.join(path, pic)
        if not check_file_resolution(pic_path, width, height):
            print('删除{}'.format(pic_path))
            os.remove(pic_path)

if __name__ == "__main__":
    path = 'D:\\Wallpaper'
    remove_low_resolution_imgs(path, 1920, 1080)
    