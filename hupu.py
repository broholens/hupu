import time
from multiprocessing import Queue
import arrow
from selenium import webdriver
from settings import DB
from settings import logging


class HuPu:

    # 每人每天最多回复自己评论数
    max_comment_count = 300

    # 本日回帖数量
    comment_count = 0

    commentary = '无限回收各种球鞋 aj 喷泡 椰子 实战  急用鞋换钱 闲置清理空间 全新二手皆可 寻求多方合作 更多精彩尽在: clpro7'

    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(30)
        self.posts = Queue()

    def store_posts(self):
        self.request('https://my.hupu.com/12173289170641/topic')
        try:
            xp = '//table[@class="mytopic topiclisttr"]//a'
            links = self.driver.find_elements_by_xpath(xp)[:30]
            posts, plates = links[::2], links[1::2]
            posts = [
                post.get_attribute('href')
                for post, plate in zip(posts, plates)
                if plate.text in '二手交易区'
            ]
            deleted = [i.get('post_url') for i in DB.deleted.find()]
            for post in set(posts).difference(set(deleted)):
                self.posts.put(post)
            logging.info('posts have been updated!')
        except:
            logging.error('update posts failed!')

    def request(self, url):
        """
        对driver.get()的封装
        """
        logging.info('requesting %s ...', url)
        try:
            self.driver.get(url)
        except:
            try:
                self.driver.execute_script('window.stop()')
            except:
                logging.error('request %s error!', url)

    def login(self, third_party):
        self.request('https://passport.hupu.com/pc/login')
        sleep_time = 10 if third_party is 'qq' else 5
        text = {'wechat': '微信登录', 'qq': 'QQ登录'}.get(third_party)
        try:
            self.driver.find_element_by_link_text(text).click()
            time.sleep(sleep_time)
            return self.driver.get_screenshot_as_base64()
        except:
            logging.error('qrcode unreachable!')
            self.driver.close()

    def is_logged(self):
        # if not os.path.exists(file):
        #     logging.info('You need to login!')
        while True:
            if self.driver.current_url in 'https://www.hupu.com/':
                break
            logging.info('current url: %s', self.driver.current_url)
            time.sleep(10)

    def comment_post(self, url, commentary):
        """
        添加评论
        """
        self.request(url)
        try:
            self.driver.find_element_by_id('atc_content').send_keys(commentary)
            self.driver.find_element_by_id('fastbtn').click()
        except:
            logging.error('find element error!')
            return

        self.comment_count += 1
        logging.info('comment count: %s', self.comment_count)

    def is_cross_bounder(self):
        now = arrow.now()
        if now.time().hour > 22 or \
                self.comment_count >= self.max_comment_count:
            time.sleep(now.shift(days=1).replace(hour=8, minute=0).timestamp
                       - now.timestamp)

    def comment_posts(self):
        self.is_logged()
        while True:
            self.is_cross_bounder()

            if self.posts.empty():
                self.store_posts()
            post = self.posts.get()
            self.comment_post(post, self.commentary)
            time.sleep(30)

            current_url = 'post.php?action=reply'
            try:
                current_url = self.driver.current_url
            except:
                self.driver.execute_script('window.stop()')
            if current_url in 'https://bbs.hupu.com/post.php?action=reply':
                logging.error('error occurs when comment %s!', post)
            else:
                logging.info('comment %s successfully!', post)
            time.sleep(150)