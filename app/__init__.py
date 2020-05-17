from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('setting.py')



db = SQLAlchemy(app)

from app.api import api
from app.admin import admin

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/admin')