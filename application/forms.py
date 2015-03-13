from flask_wtf import Form
from wtforms import TextField, BooleanField, SubmitField, PasswordField, StringField
from wtforms.validators import Required, EqualTo, Email, Length, Regexp
from wtforms import ValidationError
from application.models import User


class form_user_login(Form):
    username = TextField('username', validators = [Required()])
    password = TextField('password', validators = [Required()])
    HJ_oj = BooleanField('HJ_oj', default = True)


class form_user_register(Form):
    username = StringField('username', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                    'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('password', validators=[Required()])
    confirm = PasswordField('confirm', validators=[EqualTo('password',message="Password must match"), Required()])
    email = StringField('email', validators=[Required(),Email(), Length(1,64)])
    submit = SubmitField('submit')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already used')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already used')