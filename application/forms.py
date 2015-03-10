from flask_wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

class form_user_login(Form):
    username = TextField('username', validators = [Required()])
    password = TextField('password', validators = [Required()])
    scpc_oj = BooleanField('scpc_oj', default = True)

