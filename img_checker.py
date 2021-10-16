import cv2 as cv
import os
from PIL import Image
from io import BytesIO
from skimage.metrics import structural_similarity


def check_resolution(img_content, width, height):
    img = Image.open(BytesIO(img_content))
    _width, _height = img.size
    return _width >= width and _height >= height


def check_rate(img_content, width, height):
    img = Image.open(BytesIO(img_content))
    _width, _height = img.size
    return _width / _height == width / height


def check_file_resolution(file_path, width, height):
    img = Image.open(file_path)
    _width, _height = img.size
    return _width >= width and _height >= height


def check_file_rate(img_content, width, height):
    img = Image.open(file_path)
    _width, _height = img.size
    return _width / _height == width / height


def remove_low_resolution_imgs(path, width, height):
    for pic in os.listdir(path):
        pic_path = os.path.join(path, pic)
        if not check_file_resolution(pic_path, width, height):
            print('删除{}'.format(pic_path))
            os.remove(pic_path)


def img_similarity(path1, path2):
    img1 = cv.imread(path1)
    img2 = cv.imread(path2)
    img_gray1 = cv.cvtColor(cv.resize(img1, (64, 64)), cv.COLOR_BGR2GRAY)
    img_gray2 = cv.cvtColor(cv.resize(img2, (64, 64)), cv.COLOR_BGR2GRAY)
    score = structural_similarity(img_gray1, img_gray2)
    return score


if __name__ == "__main__":
    # path = 'D:\\Wallpaper'
    # remove_low_resolution_imgs(path, 1920, 1080)
    with open('D:\\similar.csv', 'w+') as f:
        base_img = 'C:\\Users\\liubodong\\Desktop\\Transcoded_001.jpg'
        search_dir = 'D:\\Wallpaper'
        for file_name in os.listdir(search_dir):
            file_path = os.path.join(search_dir, file_name)
            similar = img_similarity(base_img, file_path)
            f.write('{},{}\n'.format(file_path, similar))
