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

    max_comment_count = 300
    logger = logging.getLogger(__name__)
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(10)
    comment_count = 0
    post_ids = []
    # def __init__(self):
    #     self.logger = logging.getLogger(__name__)
    #     self.driver = webdriver.Firefox()
    #     self.driver.set_page_load_timeout(10)
    #     self.comment_count = 0
    #     self.post_ids = []

    def login(self, username, password):
        """
        人为滑动验证，时间为１０秒
        """
        if self.request('https://passport.hupu.com/pc/login') == 110:
            return
        try:
            self.driver.find_element_by_id('J_username').send_keys(username)
            self.driver.find_element_by_id('J_pwd').send_keys(password)
            time.sleep(10)
            self.driver.find_element_by_id('J_submit').click()
            time.sleep(1)
        except:
            self.logger.error('login error!')
            self.driver.close()

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
            # for post in self.driver.find_elements_by_xpath(xp)[2:30]:
            #     print(post.get_attribute('href'))
            #     self.comment(post.get_attribute('href'), commentary)
        except:
            posts = []
            self.logger.error('comment latest 20 error!')

        for post in posts:
            if not self.comment(post, commentary):
                self.logger.error('error occurs when comment %s!', post)
            else:
                self.logger.info('comment %s successfully!', post)
            time.sleep(120)


if __name__ == '__main__':
    hupu = HuPu()
    hupu.login('13148365571', 'i616463')
    commentary = '一切均为实拍 购买其他鞋子 降价信息 细节照片都可以咨询微信 clpro7 无限回收闲置球鞋 急用钱卖鞋的 寻求多方合作~'
    while True:
        hupu.comment_latest_20_posts(commentary)
        if hupu.comment_count > hupu.max_comment_count:
            break
    hupu.driver.close()
