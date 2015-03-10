#coding=utf-8
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_cache import Cache
from flask_admin import Admin,AdminIndexView

# Flask instance
app = Flask(__name__)
app.config.from_object('config')

# Database instance
db = SQLAlchemy(app)

# Login Manager instance
lm = LoginManager()
lm.setup_app(app)

# Cache
cache = Cache(app)

# Models
from application import models

# Views
from application import views

# Admin system
class MyBaseView(AdminIndexView):
    def is_accessible(self):
        if current_user.get_id() is None:
            return False
        return current_user.is_admin()
admin = Admin(app, name="Admin System - " + app.config['SCPC_TS_SITE_NAME'], index_view = MyBaseView(template='admin/index.html'))
from application import admins






