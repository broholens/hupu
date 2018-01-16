import time
import logging
from multiprocessing import Queue
import arrow
from selenium import webdriver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='hupu.log',
    filemode='a'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger(__name__).addHandler(console)


class HuPu:
    """
    虎扑网刷回复
    提供登录、评论功能
    """
    # 每人每天最多回复自己评论数
    max_comment_count = 300

    # 本日回帖数量
    comment_count = 0

    commentary = '一切均为实拍 购买其他鞋子 降价信息 细节照片都可以咨询微信 clpro7 无限回收闲置球鞋 急用钱卖鞋的 寻求多方合作~'

    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(30)
        self.posts = Queue()

    def wx_login(self):
        """
        微信登录
        """
        if self.request('https://passport.hupu.com/pc/login') is False:
            return
        try:
            self.driver.find_element_by_link_text('微信登录').click()
            time.sleep(5)
            return self.driver.get_screenshot_as_base64()
        except:
            logging.error('qrcode unreachable!')
            self.driver.close()

    def get_posts(self):
        if self.request('https://my.hupu.com/12173289170641/topic') is False:
            return
        try:
            xp = '//td[@class="p_title"]/a'
            posts = [
                post.get_attribute('href')
                for post in self.driver.find_elements_by_xpath(xp)[:30]
            ]
            for post in posts:
                self.posts.put(post)
        except:
            logging.error('latest 30 posts not found!')

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
            self.driver.find_element_by_id('atc_content').send_keys(commentary)
            self.driver.find_element_by_id('fastbtn').click()
        except:
            logging.error('find element error!')
            return

        self.comment_count += 1
        logging.info('comment count: %s', self.comment_count)

    def request(self, url):
        """
        对driver.get()的封装
        """
        try:
            self.driver.get(url)
        except:
            try:
                self.driver.execute_script('window.stop()')
            except:
                logging.error('request %s error!', url)
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

    # def chose_one_post(self):
    #     post_ids = [post.get('post_id') for post in TABLE.find()]
    #     if not post_ids:
    #         return
    #     return 'https://bbs.hupu.com/{}.html'.format(choice(post_ids))

    def run(self):
        # is logged
        while True:
            if self.driver.current_url in 'https://www.hupu.com/':
                break
            logging.info('current url: %s', self.driver.current_url)
            time.sleep(10)

        while True:
            if arrow.now() > arrow.now().replace(hour=23, minute=58) or \
                    self.comment_count >= self.max_comment_count:
                # 程序挂起
                time.sleep(self.sleep_time())

            if self.comment_count % 30 == 0:
                self.get_posts()

            # # 数据库中随机选一条数据
            # post = self.chose_one_post()
            # if not post:
            #     time.sleep(10)
            #     continue
            post = self.posts.get()
            self.comment(post, self.commentary)
            time.sleep(30)
            if self.driver.current_url in \
                    'https://bbs.hupu.com/post.php?action=reply':
                logging.error('error occurs when comment %s!', post)
            else:
                logging.info('comment %s successfully!', post)
            time.sleep(150)