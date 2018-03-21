from flask import render_template, url_for, redirect, session, request
from werkzeug.security import check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from .forms import LoginForm, CommentSettingsForm
from . import main
from settings import DB
from hupu import HuPu


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # sql = "SELECT username, password FROM user WHERE username = '%s'"
        # cursor.execute(sql % (form.username.data,))
        # user = cursor.fetchone()
        user = DB.user.find_one({'username': form.username.data})
        if user is not None and\
                check_password_hash(user['password'], form.password.data):
            session['username'] = user['username']
            return redirect(url_for('main.index'))
        return 'Invalid username or password'
        # flash('Invalid username or password')
    return render_template('login.html', form=form)


@main.route('/index', methods=['GET', 'POST'])
def index():
    if not session.get('username'):
        return redirect(url_for('main.login'))
    form = CommentSettingsForm()
    if form.validate_on_submit():
        hupu = HuPu()
        hupu.commentary = form.commentary.data
        hupu.max_comment_count = form.max_comment_count.data
        hupu.post_count = form.post_count.data
        hupu.topic_id = form.topic_id.data
        if form.third_party.data not in ['wechat', 'qq']:
            return 'must be wechat or qq'
        base64_img = hupu.login(form.third_party.data)
        scheduler = BackgroundScheduler()
        scheduler.add_job(hupu.comment_posts)
        scheduler.start()
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
    return render_template('index.html', form=form)