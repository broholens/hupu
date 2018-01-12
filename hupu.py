import time
import logging
from random import choice
import arrow
from selenium import webdriver
from settings import TABLE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s %(levelname)s %(message)s'
    # datefmt='%a, %d %b %Y %H:%M:%S',
    # filename='myapp.log',
    # filemode='w'
)

# headless chrome
# options = webdriver.ChromeOptions()
# # options.add_argument('--headless')
# # options.add_argument('--disable-gpu')
# # # options.add_argument("--start-maximized")
# # options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(chrome_options=options)
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

driver.set_page_load_timeout(30)
# driver.set_script_timeout(10)


class HuPu:
    """
    虎扑网刷回复
    提供登录、评论功能
    """
    # 每人每天最多回复自己评论数
    max_comment_count = 300

    logger = logging.getLogger(__name__)

    # # headless chrome
    # options = webdriver.ChromeOptions()
    # # options.add_argument('--headless')
    # # options.add_argument('--disable-gpu')
    # # options.add_argument("--start-maximized")
    # # options.add_argument('--no-sandbox')
    # driver = webdriver.Chrome(chrome_options=options)
    #
    # driver.set_page_load_timeout(10)
    # driver.set_script_timeout(10)

    # 本日回帖数量
    comment_count = 0

    def wx_login(self):
        """
        微信登录
        """
        if self.request('https://passport.hupu.com/pc/login') is False:
            return
        try:
            # wx = driver.find_element_by_link_text('微信登录')
            # wx.click()
            # return wx.get_attribute('data-href')
            driver.find_element_by_link_text('微信登录').click()
            time.sleep(5)
            return driver.get_screenshot_as_base64()
            # driver.get_screenshot_as_file('qrcode.png')
            # time.sleep(2)
        except:
            self.logger.error('qrcode unreachable!')
            driver.close()

    def comment(self, url, commentary):
        """
        添加评论
        """
        # # 自己每天最多回复自己３００条
        # if self.comment_count >= self.max_comment_count:
        #     return

        if self.request(url) is False:
            return
        try:
            driver.find_element_by_id('atc_content').send_keys(commentary)
            driver.find_element_by_id('fastbtn').click()
        except:
            self.logger.error('find element error!')
            return

        self.comment_count += 1
        self.logger.info('comment count: %s', self.comment_count)

    def request(self, url):
        """
        对driver.get()的封装
        """
        try:
            driver.get(url)
        except:
            try:
                driver.execute_script('window.stop()')
            except:
                self.logger.error('request %s error!', url)
                return False

    def sleep_time(self):
        """
        计算休眠到第二天所需时间
        """
        start = arrow.now().timestamp
        # 第二天6点开始评论
        end = arrow.now().replace(hour=6).shift(days=+1).timestamp
        # 评论数置０
        self.comment_count = 0
        return end - start

    def chose_one_post(self):
        post_ids = [post.get('post_id') for post in TABLE.find()]
        if not post_ids:
            return
        return 'https://bbs.hupu.com/{}.html'.format(choice(post_ids))

    def run(self):
        commentary = '一切均为实拍 购买其他鞋子 降价信息 细节照片都可以咨询微信 clpro7 无限回收闲置球鞋 急用钱卖鞋的 寻求多方合作~'
        # is logged
        while True:
            if driver.current_url in 'https://www.hupu.com/':
                break
            self.logger.info('current url: %s', driver.current_url)
            time.sleep(10)

        while True:
            if arrow.now() > arrow.now().replace(hour=23, minute=58) or \
                    self.comment_count >= self.max_comment_count:
                # 程序挂起
                time.sleep(self.sleep_time())

            # 数据库中随机选一条数据
            post = self.chose_one_post()
            if not post:
                time.sleep(10)
                continue

            self.comment(post, commentary)
            time.sleep(30)
            if driver.current_url in \
                    'https://bbs.hupu.com/post.php?action=reply':
                self.logger.error('error occurs when comment %s!', post)
            else:
                self.logger.info('comment %s successfully!', post)
            time.sleep(150)