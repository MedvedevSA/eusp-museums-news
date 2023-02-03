import urllib.request, json 
from urllib.parse import urljoin

from sqlalchemy.orm import Session

from db import init

urls = ['https://tes-museum.ru/']
wp_json = '/wp-json/wp/v2/posts'

def run():
    pass
    # for url_path in urls:
    #     urljoin(url_path, wp_json)
    #     with urllib.request.urlopen(urljoin(url_path, wp_json)) as url:
    #         if url.code == 200:
    #             data = json.load(url)



def main():
    init()


if __name__ == '__main__':
    main()