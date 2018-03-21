from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField, IntegerField,
    RadioField
)
from wtforms.validators import (
    DataRequired, Length, NumberRange
)
from hupu import HuPu


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CommentSettingsForm(FlaskForm):
    commentary = TextAreaField(
        label='回帖内容',
        validators=[
            DataRequired(message='必填'),
            Length(max=200, message='你好长 ^_^')
        ],
        default=HuPu.commentary
    )
    max_comment_count = IntegerField(
        label='每日最大回帖数',
        validators=[
            DataRequired(message='必填'),
            NumberRange(min=1, max=300, message='可选范围：1~300')
        ],
        default=HuPu.max_comment_count
    )
    topic_id = StringField(label='默认回复本账号帖子')

    # start_comment_at =
    # end_comment_with

    post_count = IntegerField(
        label='只回复最近多少条帖子?',
        validators=[
            NumberRange(min=1, max=40, message='可选范围：1~40')
        ],
        default=HuPu.post_count
    )

    third_party = RadioField(
        label='第三方登录',
        choices=[('qq', 'QQ'), ('wechat', '微信')],
        default='qq'
    )

    start_comment = SubmitField(label='扫码回帖')
