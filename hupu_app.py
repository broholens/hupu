import re

import web

from hupu import HuPu

urls = (
    '/login', 'login',
    '/insert/(.*?)', 'insert',
    '/delete/(.*?)', 'delete'
)

app = web.application(urls, globals())

hupu = HuPu()


class login:

    def GET(self):
        qrcode_link = hupu.wx_login()
        if not qrcode_link:
            return 'qrcode link unreachable'
        raise web.seeother(qrcode_link)


class insert:
    def GET(self, posts):
        for post_id in re.findall('\d+', posts):
            hupu.post_ids.add(post_id)
        return {
            number: post_id
            for number, post_id in enumerate(hupu.post_ids)
        }


class delete:
    def GET(self, posts):
        for post_id in re.findall('\d+', posts):
            hupu.post_ids.remove(post_id)
        return {
            number: post_id
            for number, post_id in enumerate(hupu.post_ids)
        }


if __name__ == '__main__':
    app.run()
