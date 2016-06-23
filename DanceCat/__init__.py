from flask import Flask
from Constants import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

app.config.from_object('config')
config = app.config
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.session_protection = "strong"
lm.login_message = "Please log in to continue!"
lm.login_message_category = "alert-danger"

from DanceCat import Models, Views, ErrorViews