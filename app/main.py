from crawler.fb_crawler import FacebookCrawlerPool

from time import time, sleep
from flask import Flask


if __name__ == '__main__':
    # app = Flask(__name__)
    # app.run('0.0.0.0', 5001)

    crawler = FacebookCrawlerPool('data/users.txt', 'data/targets.txt')
    
    while True:
        crawler.start()
        time.sleep(1800)