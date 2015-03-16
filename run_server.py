#!flask/bin/python
from application import app
from flask_script import Manager
from flask_bootstrap import Bootstrap

#app.run(debug = True)
#use python debug.py runserver --host 0.0.0.0, so other computer can access
manager = Manager(app)
bootstrap = Bootstrap(app)

if __name__=="__main__":
    manager.run()
