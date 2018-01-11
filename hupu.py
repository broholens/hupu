import time
import logging
from selenium import webdriver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s %(levelname)s %(message)s'
    # datefmt='%a, %d %b %Y %H:%M:%S',
    # filename='myapp.log',
    # filemode='w'
)


class HuPu:
    """
    虎扑网刷回复
    提供登录、评论功能
    需要人为滑动验证登录
    """
    # 每人每天最多回复自己评论数
    max_comment_count = 300

    logger = logging.getLogger(__name__)

    # headless chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(chrome_options=options)

    driver.set_page_load_timeout(10)

    # 本日回帖数量
    comment_count = 0

    # 帖子id
    post_ids = set()

    def wx_login(self):
        """
        微信登录
        """
        if self.request('https://passport.hupu.com/pc/login') == 110:
            return
        try:
            return self.driver.find_element_by_link_text('微信登录')\
                .get_attribute('data-href')
        except:
            self.logger.error('qrcode unreachable!')
            self.driver.close()

    def comment(self, url, commentary):
        """
        添加评论
        """
        # 自己每天最多回复自己３００条
        if self.comment_count >= self.max_comment_count:
            return

        if self.request(url) == 110:
            return
        try:
            self.driver.find_element_by_id('atc_content').send_keys(commentary)
            self.driver.find_element_by_id('fastbtn').click()
        except:
            self.logger.error('find element error!')
            return

        self.comment_count += 1
        self.logger.info('comment count: %s', self.comment_count)
        return 'ok'

    def request(self, url):
        """
        对driver.get()的封装
        １１０仅用做判断是否成功访问，本身并无意义
        """
        try:
            self.driver.get(url)
            time.sleep(1)
        except:
            try:
                self.driver.execute_script('window.stop()')
            except:
                self.logger.error('request %s error!', url)
                return 110

    def comment_latest_20_posts(self, commentary):
        if self.request('https://my.hupu.com/12173289170641/topic') == 110:
            return
        try:
            xp = '//td[@class="p_title"]/a'
            posts = [
                post.get_attribute('href')
                for post in self.driver.find_elements_by_xpath(xp)[:30]
            ]
        except:
            posts = []
            self.logger.error('comment latest 20 error!')

        for post in posts:
            if not self.comment(post, commentary):
                self.logger.error('error occurs when comment %s!', post)
            else:
                self.logger.info('comment %s successfully!', post)
            time.sleep(120)

#
# if __name__ == '__main__':
#     hupu = HuPu()
#     hupu.wx_login()
#     commentary = '一切均为实拍 购买其他鞋子 降价信息 细节照片都可以咨询微信 clpro7 无限回收闲置球鞋 急用钱卖鞋的 寻求多方合作~'
#     while True:
#         hupu.comment_latest_20_posts(commentary)
#         if hupu.comment_count > hupu.max_comment_count:
#             break
#     hupu.driver.close()
