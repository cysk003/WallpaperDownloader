from datetime import date
import requests
from bs4 import BeautifulSoup

base_url = "http://28th.cc/"
main_url = base_url + 'forum-181-{}.html'

conf_path = 'thz.date'
last_date = ''

def update_date() -> None:
    with open(conf_path, 'w+') as f:
        f.write(last_date)
        f.flush()
        f.close()

def get_last_date() -> str:
    with open(conf_path, 'r') as f:
        last_date = f.readline()
        f.close()
        return last_date

last_date = get_last_date()
if not last_date:
    today = date.today()
    last_date = today.strftime('%Y-%m-%d')
    update_date()

print('last_date is ' + last_date)

session = requests.Session()

index = 1
running = True
last_article_date = None
while running:
    article_list_url = main_url.format(index)
    content = session.get(article_list_url).text
    soup = BeautifulSoup(content, 'html.parser')
    separatorline = soup.find(id='separatorline')
    list = separatorline.find_all_next('a', class_='s xst')
    for article in list:
        article_title = article.text
        article_date = article_title.split(' ')[0]
        if article_date <= last_date:
            running = False
            break
        if not last_article_date or article_date > last_article_date:
            last_article_date = article_date
        if article_date > last_date:
            article_url = base_url + article['href']
            article_content = str(session.get(article_url).content, 'utf-8')
            article_soup = BeautifulSoup(article_content, 'html.parser')
            download_a = article_soup.find('a', id=True, onclick="showWindow('imc_attachad', this.href)")
            download_href = download_a['href']
            aid = download_href.split('?')[1].split('=')[1]
            torren_link = base_url + "forum.php?mod=attachment&aid=" + aid
            print(torren_link)
    index += 1

last_date = last_article_date
print('last_date updated to ' + last_date)
update_date()
    

