import time
from multiprocessing import Queue
import arrow
from selenium import webdriver
from settings import DB, logger, send_email


class HuPu:

    # 每人每天最多回复自己评论数
    max_comment_count = 300

    # 本日回帖数量
    comment_count = 0

    commentary = '无限回收各种球鞋 aj 喷泡 椰子 实战 急用鞋换钱 闲置清理空间 全新二手皆可 打包优先 寻求多方合作 更多精彩尽在: clpro7'

    topic_id = None

    start_at = 8

    end_with = 23

    post_count = 30

    def __init__(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_page_load_timeout(30)
        self.posts = Queue()

    def get_posts_address(self):
        if not self.topic_id:
            self.topic_id = self.driver.find_element_by_id('g_m').get_attribute('iuid')
        self.posts_address = 'https://my.hupu.com/{}/topic'.format(self.topic_id)

    def store_posts(self):
        self.request(self.posts_address)
        try:
            xp = '//table[@class="mytopic topiclisttr"]//a'
            links = self.driver.find_elements_by_xpath(xp)[:self.post_count*2]
            posts, plates = links[::2], links[1::2]
            posts = [
                post.get_attribute('href')
                for post, plate in zip(posts, plates)
                if plate.text in ['二手交易区']
            ]
            deleted = [i.get('post_url') for i in DB.deleted.find()]
            # set无序 所以无序回帖
            for post in set(posts).difference(set(deleted)):
                self.posts.put(post)
            logger.info('posts have been updated!')
        except:
            logger.error('update posts failed!')

    def request(self, url):
        try:
            self.driver.get(url)
        except:
            self.driver.execute_script('window.stop()')

    def login(self, third_party):
        self.request('https://passport.hupu.com/pc/login')
        sleep_time = 8  # if third_party is 'qq' else 5
        text = {'wechat': '微信登录', 'qq': 'QQ登录'}.get(third_party)
        try:
            self.driver.find_element_by_link_text(text).click()
            time.sleep(sleep_time)
            return self.driver.get_screenshot_as_base64()
        except:
            logger.error('二维码获取失败!')
            self.driver.close()

    def is_logged(self):
        while True:
            if self.driver.current_url in 'https://www.hupu.com/':
                self.get_posts_address()
                send_email(f'登陆成功!开始回帖{self.posts_address}')
                break
            time.sleep(10)

    def comment_post(self, url, commentary):
        """添加评论"""
        self.request(url)
        try:
            self.driver.find_element_by_id('atc_content').send_keys(commentary)
            self.driver.find_element_by_id('fastbtn').click()
        except:
            logger.error('find element error!')
            send_email(f'评论{url}时出错')

    def is_boundary(self):
        now = arrow.now()
        if now.time().hour == self.end_with or \
                self.comment_count >= self.max_comment_count:
            logger.info('%s 开始休眠, 明天%s点再回帖', now, self.start_at)
            send_email('开始休眠')
            time.sleep((now.shift(days=1).replace(hour=self.start_at, minute=0) - now).seconds)
            send_email('开始回帖')
            self.comment_count = 0

    def comment_posts(self):
        self.is_logged()
        while True:
            self.is_boundary()

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
                logger.error('提交回帖请求时出错 %s!', post)
                send_email(f'提交回帖请求时出错{post}')
            else:
                self.comment_count += 1
                logger.info('评论 %s 成功!　已评论: %s', post, self.comment_count)
            time.sleep(150)
