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

class EnumFieldEnum(enum.Enum):
    val0 = 0
    val1 = 1

class Test1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    str_field_fixed_length = db.Column(db.String(128), nullable=False)
    txt_field = db.Column(db.Text, nullable=False)
    date_field_now = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    int_field = db.Column(db.Integer)
    bool_field = db.Column(db.Boolean, nullable=False)
    float_field = db.Column(db.Float, nullable=False)
    enum_field = db.Column(db.Enum(EnumFieldEnum), nullable=False)

    test2_id = db.Column(db.Integer, db.ForeignKey('test2.id'), nullable=False)
    test2 = db.relationship("Test2", backref=db.backref("tests1", lazy=True))

    def __repr__(self):
        return "Test1 {}".format(self.str_field_fixed_length)

class Test2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    str_field_fixed_length = db.Column(db.String(256), nullable=False)


    def __repr__(self):
        return "Test2 {}".format(self.str_field_fixed_length)

admin = Admin(app, name='test', template_mode='bootstrap3')

admin.add_view(ModelView(Test1, db.session))
admin.add_view(ModelView(Test2, db.session))

if __name__ == '__main__':
    app.run()