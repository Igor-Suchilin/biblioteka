from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__) # создание образца класса фласк
app.secret_key = '111' # создание секретного ключа администратора
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteka.db' # ссылка на базу данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # отключение сообщения о скором прекращении поддержки
db = SQLAlchemy(app) # создание базы данных
manager = LoginManager(app) # создание администрации

from sweater import models, routes

db.create_all() # развертывание базы данных