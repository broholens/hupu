import time
import logging
from multiprocessing import Queue
from requestium import Session
from settings import DB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='hupu.log',
    filemode='w'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


class HuPu:

    # 每人每天最多回复自己评论数
    max_comment_count = 300

    # 本日回帖数量
    comment_count = 0

    commentary = '一切均为实拍 购买其他鞋子 降价信息 细节照片都可以咨询微信 clpro7 无限回收闲置球鞋 急用钱卖鞋的 寻求多方合作~'

    def __init__(self):
        self.s = Session(
            webdriver_path='/usr/local/share/chromedriver',
            browser='chrome',
            default_timeout=30,
            webdriver_options={'arguments': ['headless']}
        )
        self.posts = Queue()

    def store_posts(self):
        response = self.s.get('https://my.hupu.com/12173289170641/topic')
        try:
            links = response.xpath('//table[@class="mytopic topiclisttr"]//a')
            posts, plates = links[::2], links[1::2]
            posts = [
                post.get_attribute('href')
                for post, plate in zip(posts, plates)
                if plate.text in '二手交易区'
            ]
            deleted = [i.get('post_url') for i in DB.deleted.find()]
            for post in set(posts).difference(set(deleted)):
                DB.hupu.update_one(
                    {'post_url': post},
                    {
                        '$set': {'post_url': post},
                        '$currentDate': {'update': True}
                    },
                    upsert=True
                )
            logging.info('posts have been updated!')
        except:
            logging.error('update posts failed!')

    def login(self, third_party):
        self.s.driver.get('https://passport.hupu.com/pc/login')
        text = {'wechat': '微信登录', 'qq': 'QQ登录'}.get(third_party)
        try:
            self.s.driver.ensure_element_by_link_text(text).click()
            time.sleep(5)
            return self.s.driver.get_screenshot_as_base64()
        except:
            logging.error('qrcode unreachable!')
            self.s.close()

    def is_logged(self):
        while True:
            if self.s.driver.current_url in 'https://www.hupu.com/':
                break
            logging.info('current url: %s', self.s.driver.current_url)
            time.sleep(10)

    def comment_post(self, url, commentary):
        """
        添加评论
        """
        self.s.driver.get(url)
        try:
            self.s.driver.ensure_element_by_id('atc_content').send_keys(commentary)
            self.s.driver.ensure_element_by_id('fastbtn').ensure_click()
        except:
            logging.error('find element error!')
            return

        self.comment_count += 1
        logging.info('comment count: %s', self.comment_count)

    def get_posts(self, count=30):
        for post in DB.hupu.find().sort([('update', -1)]).limit(count):
            self.posts.put(post.get('post_url'))

    def comment_posts(self):
        while True:
            if self.comment_count >= self.max_comment_count:
                break

            if self.posts.empty():
                self.get_posts()
            post = self.posts.get()

            self.comment_post(post, self.commentary)
            time.sleep(30)

            current_url = 'post.php?action=reply'
            try:
                current_url = self.s.driver.current_url
            except:
                self.s.driver.execute_script('window.stop()')
            if current_url in 'https://bbs.hupu.com/post.php?action=reply':
                logging.error('error occurs when comment %s!', post)
            else:
                logging.info('comment %s successfully!', post)
            time.sleep(150)
# class HuPu:
#     """
#     虎扑网刷回复
#     提供登录、评论功能
#     """
#     # 每人每天最多回复自己评论数
#     max_comment_count = 300
#
#     # 本日回帖数量
#     comment_count = 0
#
#     commentary = '一切均为实拍 购买其他鞋子 降价信息 细节照片都可以咨询微信 clpro7 无限回收闲置球鞋 急用钱卖鞋的 寻求多方合作~'
#
#     def __init__(self):
#         options = webdriver.FirefoxOptions()
#         options.add_argument('--headless')
#         self.driver = webdriver.Firefox(options=options)
#         self.driver.set_page_load_timeout(30)
#         self.posts = Queue()
#
#     def wx_login(self):
#         """
#         微信登录
#         """
#         if self.request('https://passport.hupu.com/pc/login') is False:
#             return
#         try:
#             self.driver.find_element_by_link_text('微信登录').click()
#             time.sleep(5)
#             return self.driver.get_screenshot_as_base64()
#         except:
#             logging.error('qrcode unreachable!')
#             self.driver.close()
#
#     def store_posts(self):
#         if self.request('https://my.hupu.com/12173289170641/topic') is False:
#             return
#         try:
#             xp = '//td[@class="p_title"]/a'
#             posts = [
#                 post.get_attribute('href')
#                 for post in self.driver.find_elements_by_xpath(xp)[:30]
#             ]
#             deleted = [i.get('post_url') for i in DB.deleted.find()]
#             for post in set(posts).difference(set(deleted)):
#                 DB.hupu.update_one(
#                     {'post_url': post},
#                     {
#                         '$set': {'post_url': post},
#                         '$currentDate': {'update': True}
#                     },
#                     upsert=True
#                 )
#             logging.info('got latest 30!')
#         except:
#             logging.error('latest 30 posts not found!')
#
#     def comment(self, url, commentary):
#         """
#         添加评论
#         """
#         # # 自己每天最多回复自己３００条
#         # if self.comment_count >= self.max_comment_count:
#         #     return
#
#         if self.request(url) is False:
#             return
#         try:
#             self.driver.find_element_by_id('atc_content').send_keys(commentary)
#             self.driver.find_element_by_id('fastbtn').click()
#         except:
#             logging.error('find element error!')
#             return
#
#         self.comment_count += 1
#         logging.info('comment count: %s', self.comment_count)
#
#     def request(self, url):
#         """
#         对driver.get()的封装
#         """
#         logging.info('requesting %s ...', url)
#         try:
#             self.driver.get(url)
#         except:
#             try:
#                 self.driver.execute_script('window.stop()')
#             except:
#                 logging.error('request %s error!', url)
#                 return False
#
#     def sleep_time(self):
#         """
#         计算休眠到第二天所需时间
#         """
#         start = self.now.timestamp
#         # 第二天6点开始评论
#         end = self.now.replace(hour=6).shift(days=+1).timestamp
#         # 评论数置０
#         self.comment_count = 0
#         return end - start
#
#     def get_posts(self):
#         """
#         从数据库中选择最近30条, 评论完需要时间 30*3=90min
#         """
#         self.store_posts()
#         for post in DB.hupu.find().sort([('update', -1)]).limit(30):
#             self.posts.put(post.get('post_url'))
#
#     def run(self):
#         # is logged
#         while True:
#             if self.driver.current_url in 'https://www.hupu.com/':
#                 break
#             logging.info('current url: %s', self.driver.current_url)
#             time.sleep(10)
#
#         while True:
#             self.now = arrow.now()
#             if self.now > self.now.replace(hour=23, minute=55) or \
#                     self.comment_count >= self.max_comment_count:
#                 # 程序挂起
#                 time.sleep(self.sleep_time())
#
#             if self.posts.empty():
#                 self.get_posts()
#             post = self.posts.get()
#
#             self.comment(post, self.commentary)
#             time.sleep(30)
#
#             current_url = 'post.php?action=reply'
#             try:
#                 current_url = self.driver.current_url
#             except:
#                 self.driver.execute_script('window.stop()')
#             if current_url in 'https://bbs.hupu.com/post.php?action=reply':
#                 logging.error('error occurs when comment %s!', post)
#             else:
#                 logging.info('comment %s successfully!', post)
#             time.sleep(150)
