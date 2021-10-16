import requests
from requests.adapters import HTTPAdapter
from os import path
import os
import urllib3
import signal
import time

urllib3.disable_warnings()

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

save_path = path.join(os.environ['HOME'], 'Pictures')
dir_name = 'wallhaven'
save_dir = path.join(save_path, dir_name)
if not path.exists(save_dir):
    os.makedirs(save_dir)

save_path = save_path = os.path.join(save_path, dir_name)

def get_pictures(url: str) -> list:
    pic_urls = []
    response = session.get(url, timeout=(10, 10))
    if response.status_code == 200:
        js = response.json()
        for p in js["data"]:
            pic_urls.append({"id": p["id"], "path": p["path"]})
    else:
        print("Get None, Code: {}".format(response.status_code))
    return pic_urls


if __name__ == "__main__":

    running = True

    def stop(signum, stack):
        print("Received signal: {}, prepare to stop".format(signum))
        global running
        running = False

    signal.signal(signal.SIGINT, stop)

    # "1d", "3d", "1w", "1M", "3M", "6M", "1y"
    for top_range in ["1y", "6M", "3M", "1M", "1w", "3d", "1d"]:
        page = 1
        api_url = "https://wallhaven.cc/api/v1/search?apikey=OmD6tOzHlGge3MQzmxgKTnSBCpBq86gp&categories=111&purity=111&order=desc&sorting=toplist&topRange={}&atleast=1920x1080&page={}"
        while running:
            url = api_url.format(top_range, page)
            print(url)
            pics = get_pictures(url)
            print("Get {} pictures".format(len(pics)))
            if not pics:
                break
            for pic in pics:
                pic_id = pic["id"]
                pic_url = pic["path"]
                parent_dir = os.path.join(save_path, pic_id[:2])
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
                pic_save_path = os.path.join(
                    parent_dir, "{}.{}".format(pic_id, pic_url.split(".")[-1]))
                if os.path.exists(pic_save_path):
                    print("{} already exists".format(pic_save_path))
                    continue
                pic_response = session.get(pic_url, timeout=(10, 10))
                if pic_response.status_code == 200:
                    with open(pic_save_path, "wb+") as f:
                        f.write(pic_response.content)
                        f.flush()
                        print("Download {} to {}".format(
                            pic_url, pic_save_path))
            page += 1
            time.sleep(2)
