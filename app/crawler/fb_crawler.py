import os
import sys
from selenium import webdriver
import time
import datetime
import random
import re
import json
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.getcwd())
from utils.extractor_utils import time_extractor
# from utils.log import create_log
from config.fb_config import BaseConfig
# from data.db import crawled_post


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


def wait(delta):
    time.sleep(random.uniform(delta/2, delta))


class FacebookCrawler:

    def __init__(self, username, password):
        """
        article [
            {
                url: (str) 
                author: (str) id of author
                time: (int) time stamp
                content: (str)
                image: [] list of image sources
            }
        ]
        """
        desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy() 
        desired_capabilities['acceptInsecureCerts'] = True

        options = webdriver.ChromeOptions()
        options.add_argument("disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        # options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

        # driver = webdriver.Chrome(driver_path, options=options, desired_capabilities=desired_capabilities)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, desired_capabilities=desired_capabilities)

        self.config = BaseConfig

        self.username = username
        self.password = password
        self.articles = []
        self.driver = driver
        self.login()
        self.valid = True

    
    def login(self):
        try:
            self.driver.get("https://facebook.com/")
            self.driver.find_element_by_name("email").send_keys(self.username)
            self.driver.find_element_by_name("pass").send_keys(self.password)
            self.driver.find_element_by_name("login").click()
        except Exception as ex:
            logging.error(f'{datetime.datetime.now}: {str(traceback.format_exc())}')
            print(traceback.format_exc())
            self.valid = False

        if 'checkpoint' in self.driver.current_url:
            self.valid = False

    def pass_save_device(self):
        if "save-device" in self.driver.current_url:
            self.driver.find_element_by_class_name("bk").click()


    def get_articles(self, user_id):
        logging.info(f'{self.username} is crawling user {user_id}...')
        print(f'{self.username} is crawling user {user_id}...')
        wait(2)
        if 'https' in user_id:
            self.driver.get(user_id)
        self.driver.get(f"https://facebook.com/{user_id}")
        self.config.SCROLL_PAUSE_TIME = 0.5
        for _ in range(5):
            self.driver.execute_script(f"window.scrollTo(0, {(_+1)*540});")
            time.sleep(self.config.SCROLL_PAUSE_TIME)

        wait(5)
        for i in range(1, self.config.NUM_POSTS):
            url = ''
            try:
                url = self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
            except Exception as ex:
                try:
                    url = self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
            #                                         /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a
            #                                         /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a
                except:
                    logging.error(f'{datetime.datetime.now}: {str(traceback.format_exc())}')
            if url in crawled_post:
                break
            try:
                action = webdriver.ActionChains(self.driver)
                action.move_to_element(url).key_down(Keys.CONTROL).click().perform()
                wait(2)
            except AttributeError:
                logging.error(f'{datetime.datetime.now}: {str(traceback.format_exc())}')
                self.valid = False
                return
        initial_window = self.driver.window_handles[0]
        for window in self.driver.window_handles:
            self.driver.switch_to.window(window)
            url = str(self.driver.current_url)
            if 'posts' not in url and 'watch' not in url:
                continue
            logging.info(f'\t{datetime.datetime.now}: Crawling post {url}...')
            print(f'\tCrawling post {url}...')
            wait(self.config.POST_PAUSE_TIME)

            author = re.search('(?<=com/)([\w.])*', self.driver.current_url).group()
            content = ''
            try:
                content = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]/div[1]/div/div/div/span').text
            except Exception as ex:
                logging.error(f'{datetime.datetime.now}: {str(traceback.format_exc())}')
                print(str(ex))
                # create_log(str(ex))
            created_date = 0
            try:
                created_date = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b').text
                created_date = time_extractor(created_date)
            except Exception as ex:
                logging.error(f'{datetime.datetime.now}: {str(traceback.format_exc())}')
                print(str(ex))
                # create_log(str(ex))
            imgs = []
            try:
                imgs = self.driver.find_elements_by_tag_name('img')
                imgs = [i.get_attribute('src') for i in imgs]
                imgs = filter(lambda a: 'https' in a, imgs)
                imgs = list(set(imgs))
            except Exception as ex:
                logging.error(f'{datetime.datetime.now}: {str(traceback.format_exc())}')
                print(str(ex))
                # create_log(str(ex))
            self.articles.append({
                'url':url,
                'author':author,
                'content':content,
                'created_date':created_date,
                'imgs':imgs
            })
            wait(self.config.POST_PAUSE_TIME)
            self.driver.close()
        self.driver.switch_to.window(initial_window)
        self.export_articles(user_id)
        return 


    def export_articles(self, user_id, dir='output'):
        with open(f"{dir}/{user_id}.json", "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False)
            self.articles.clear()


class FacebookCrawlerPool:

    def __init__(self, user_file, target_file):
        self.crawlers = []
        self.__init_crawlers(user_file)
        self.targets = open(target_file, 'r').read().split('\n')
        
    
    def __init_crawlers(self, user_file):
        with open(user_file, 'r') as f:
            users = f.read().split('\n')
            for user in users:
                username = user.split()[0]
                password = user.split()[1]
                self.crawlers.append(FacebookCrawler(username, password))


    def start(self):
        id = 0
        for target in self.targets:
            crawler = self.crawlers[id]
            # while crawler.valid is False:
            #     print(f'Remove account {crawler.username}')
            #     self.crawlers.remove(crawler)
            #     if len(self.crawlers) == 0:
            #         print(f'All accounts have been banned!')
            #         return
            #     id %= len(self.crawlers)
            #     crawler = self.crawlers[id]

            self.crawlers[id].get_articles(target)

        for crawler in self.crawlers:
            crawler.driver.quit()