#!/usr/bin/python3

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import enum
from datetime import datetime

app = Flask(__name__)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['TESTING'] = True
app.config['SECRET_KEY'] = '0123456789'

db = SQLAlchemy(app)
