import os
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import ast 
import logging
import time
import inspect
import re
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append(os.getcwd())
print(os.getcwd())
from utils.extractor_utils import time_extractor
from utils.log import create_log


def wait(delta):
    time.sleep(random.uniform(1, delta))


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
        driver_path = "resources/selenium_drivers/chromedriver"
        print(driver_path)
        options.add_argument("disable-infobars")
        options.add_argument("--disable-notifications")
        # options.add_argument('--no-sandbox')
        # options.add_argument("--headless")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(driver_path, options=options, desired_capabilities=desired_capabilities)
        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, desired_capabilities=desired_capabilities)

        self.username = username
        self.password = password
        self.articles = []
        self.driver = driver
        self.login()

    
    def login(self):
        self.driver.get("https://facebook.com/")
        self.driver.find_element_by_name("email").send_keys(self.username)
        self.driver.find_element_by_name("pass").send_keys(self.password)
        self.driver.find_element_by_name("login").click()


    def pass_save_device(self):
        if "save-device" in self.driver.current_url:
            self.driver.find_element_by_class_name("bk").click()


    def get_articles(self, user_id):
        wait(2)
        if 'https' in user_id:
            self.driver.get(user_id)
        self.driver.get(f"https://facebook.com/{user_id}")
        SCROLL_PAUSE_TIME = 0.5
        for _ in range(5):
            self.driver.execute_script(f"window.scrollTo(0, {(_+1)*540});")
            time.sleep(SCROLL_PAUSE_TIME)

        wait(5)
        for i in range(1, 10):
            url = ''
            try:
                url = self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
            except Exception as ex:

                url = self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[{i}]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
            #                                         /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a
            #                                         /html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[1]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a
            action = webdriver.ActionChains(self.driver)
            action.move_to_element(url).key_down(Keys.CONTROL).click().perform()
            wait(2)

        current_window = self.driver.current_window_handle
        for window in self.driver.window_handles:
            if window == current_window:
                continue
            self.driver.switch_to.window(window)
            url = str(self.driver.current_url)
            if 'posts' not in url or 'watch' not in url:
                continue
            print(f'Crawling {url}')
            wait(2)

            author = re.search('(?<=com/)([\w.])*', self.driver.current_url).group()
            content = ''
            try:
                content = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]/div[1]/div/div/div/span').text
            except Exception as ex:
                create_log(str(ex))
            created_date = 0
            try:
                created_date = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b').text
                created_date = time_extractor(created_date)
            except Exception as ex:
                create_log(str(ex))
            imgs = []
            try:
                imgs = self.driver.find_elements_by_tag_name('img')
                imgs = [i.get_attribute('src') for i in imgs]
            except Exception as ex:
                create_log(str(ex))
            self.articles.append({
                'url':url,
                'author':author,
                'content':content,
                'created_date':created_date,
                'imgs':imgs
            })
            self.driver.close()
        return 


    def export_articles(self, user_id):
        with open(f"{user_id} articles.json", "w", encoding="utf-8") as f:
            json.dump(self.articles, f, ensure_ascii=False)

