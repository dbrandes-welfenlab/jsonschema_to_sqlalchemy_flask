#!/usr/bin/python3

from result import db
db.create_all()
db.session.commit()

