"""
目前只有登录功能有用　　2018.1.16
"""

import re
import web
from hupu import HuPu
from settings import DB

urls = (
    '/hupu/login', 'login',
    # 'hupu/insert/(.*?)', 'insert',
    '/hupu/delete/(.*?)', 'delete'
)

app = web.application(urls, globals())

hp = HuPu()


class login:

    def GET(self):
        base64_img = hp.wx_login()
        # if not os.path.exists('qrcode.png'):
        #     return 'qrcode unreachable'
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>wechat login</title>
            </head>
            <body>
                <div style="text-align: center">
                    <img src="data:image/png;base64,{}" style="margin: 0 auto; display: block;">
                </div>
            </body>
            </html>        
        """.format(base64_img)
        # raise web.seeother(qrcode_link)


# class insert:
#     def GET(self, posts):
#         for post_id in re.findall('\d+', posts):
#             TABLE.update_one(
#                 {'post_id': post_id},
#                 {'$set': {'post_id': post_id}},
#                 upsert=True
#             )
#         return {
#             number: post_id.get('post_id')
#             for number, post_id in enumerate(TABLE.find())
#         }
#
#
class delete:
    def GET(self, posts):
        for post_id in re.findall('\d+', posts):
            DB.hupu.delete_one({'post_url': {'$regex': post_id}})
            DB.deleted.update_one(
                {'post_url': post_id},
                {
                    '$set': {'post_url': post_id},
                    '$currentDate': {'update': True}
                },
                upsert=True
            )

        return {
            number: post_id.get('post_url')
            for number, post_id in
            enumerate(DB.find().sort([('update', -1)]).limit(30))
        }
