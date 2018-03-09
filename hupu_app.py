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
        return 'ok'