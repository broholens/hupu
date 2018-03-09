import re
from flask import Flask
from hupu import HuPu
from settings import DB

app = Flask(__name__)

hupu = HuPu()


@app.route('/hupu/login/<third_party>')
def login(third_party):
    if third_party not in ['wechat', 'qq']:
        return 'must be wechat or qq'
    base64_img = hupu.login(third_party)
    return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>hupu login</title>
        </head>
        <body>
            <div style="text-align: center">
                <img src="data:image/png;base64,{}" style="margin: 0 auto; display: block;">
            </div>
        </body>
        </html>
        """.format(base64_img)


@app.route('/hupu/delete/<posts_id>')
def delete(posts_id):
    for post_id in re.findall('\d+', posts_id):
        post_id = 'https://bbs.hupu.com/{}.html'.format(post_id)
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
            enumerate(DB.hupu.find().sort([('update', -1)]).limit(30))
        }

# urls = (
#     '/hupu/login', 'login',
#     # 'hupu/insert/(.*?)', 'insert',
#     '/hupu/delete/(.*?)', 'delete'
# )
#
# app = web.application(urls, globals())
#
# hp = HuPu()
#
#
# class login:
#
#     def GET(self):
#         base64_img = hp.wx_login()
#         # if not os.path.exists('qrcode.png'):
#         #     return 'qrcode unreachable'
#         return """
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <title>wechat login</title>
#             </head>
#             <body>
#                 <div style="text-align: center">
#                     <img src="data:image/png;base64,{}" style="margin: 0 auto; display: block;">
#                 </div>
#             </body>
#             </html>
#         """.format(base64_img)
#         # raise web.seeother(qrcode_link)
#
#
# # class insert:
# #     def GET(self, posts):
# #         for post_id in re.findall('\d+', posts):
# #             TABLE.update_one(
# #                 {'post_id': post_id},
# #                 {'$set': {'post_id': post_id}},
# #                 upsert=True
# #             )
# #         return {
# #             number: post_id.get('post_id')
# #             for number, post_id in enumerate(TABLE.find())
# #         }
# #
# #
# class delete:
#     def GET(self, posts):
#         for post_id in re.findall('\d+', posts):
#             DB.hupu.delete_one({'post_url': {'$regex': post_id}})
#             DB.deleted.update_one(
#                 {'post_url': post_id},
#                 {
#                     '$set': {'post_url': post_id},
#                     '$currentDate': {'update': True}
#                 },
#                 upsert=True
#             )
#
#         return {
#             number: post_id.get('post_url')
#             for number, post_id in
#             enumerate(DB.hupu.find().sort([('update', -1)]).limit(30))
#         }
