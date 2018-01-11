import re

import web

from hupu import HuPu
from settings import DB

urls = (
    '/login', 'login',
    '/insert/(.*?)', 'insert',
    '/delete/(.*?)', 'delete'
)

app = web.application(urls, globals())

hupu = HuPu()


class login:

    def GET(self):
        # qrcode_link = hupu.wx_login()
        qrcode_link = 'https://www.baidu.com'
        if not qrcode_link:
            return 'qrcode link unreachable'
        raise web.seeother(qrcode_link)


class insert:
    def GET(self, posts):
        hupu.post_ids.extend(re.findall('\d+', posts))
        return {
            number: post_link
            for number, post_link in enumerate(hupu.post_ids)
        }


class delete:
    def GET(self, posts):
        pass


if __name__ == '__main__':
    app.run()
