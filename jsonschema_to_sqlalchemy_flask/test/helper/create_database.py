#!/usr/bin/python3
import os
from jsonschema_to_sqlalchemy_flask.test.expected_output.result import db

def delete_and_recreate_database():
    try:
        os.remove("/tmp/json_schema_to_sqlalchemy_flask_test.db")
    except FileNotFoundError:
        pass
    db.create_all()
    db.session.commit()

if __name__ == "__main__":
    delete_and_recreate_database()
