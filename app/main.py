from crawler.fb_crawler import FacebookCrawler

from time import time, sleep
from flask import Flask


if __name__ == '__main__':
    # app = Flask(__name__)
    # app.run('0.0.0.0', 5001)
    crawler = FacebookCrawler('100072986628485', '@@q3rajMm2524857')
    ids = open('data/targets.txt', 'r').read().split('\n')
    crawled = open('data/post.txt', 'r').read().split()
    while True:
        for id in ids:
            print(f'Crawling {id}')
            crawler.get_articles(id)
            crawler.export_articles(id)