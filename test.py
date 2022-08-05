#!/usr/bin/python3

import unittest
import difflib
import json

from src.convert_to_sqlalchemy_flask import insert_from_file
from src.convert_from_json_schema import convert_flask_admin
from test.helper.create_database import delete_and_recreate_database
from test.expected_output.create_from_json import create_from_json
from test.expected_output.dump_to_json import dump_to_json

def check_diff(txt1, txt2):
    diff = difflib.ndiff(txt1.splitlines(), txt2.splitlines())
    equal = True
    lines = []
    for line in diff:
        lines.append(line)
        if line.startswith("+") or line.startswith("-"):
            equal = False
    if not equal:
        for line in lines:
            print(line)
    return equal
    
def json_load(filename):
    with open(filename) as filehandle:
        return json.load(filehandle)

converted_filename = "test/expected_output/converted.json"
expected_filename = "test/expected_output/result.py"
name_filename_pk_list = [
    {"name": "test2", "data": "test/data/test2.json","pk": "test2"},
    {"name": "test1", "data": "test/data/test1.json","pk": "test1"}] #Order is important!
schema_filename_list = ["test/data/test1.schema.json", "test/data/test2.schema.json"]


class TestJsonSchemaToSQLAlchemy(unittest.TestCase):
    def test_to_sql_alchemy(self):
        self.maxDiff = None
        res_data = insert_from_file(converted_filename)
        with open(expected_filename) as expected_file:
            expected = expected_file.read()
        files_equal = check_diff(res_data, expected)
        self.assertTrue(files_equal)
        
    def test_from_json_schema(self):
        self.maxDiff = None
        res_data = convert_flask_admin(schema_filename_list)
        converted = json_load(converted_filename)
        if converted != res_data:
            with open("/tmp/json_schema_to_sqlalchemy_flask_res_data.json","w") as fh:
                fh.write(json.dumps(res_data))
        self.assertEqual(converted,res_data)
        
    def test_run_test_expected(self):
        delete_and_recreate_database()
        create_from_json(name_filename_pk_list, json_load)
        for d in name_filename_pk_list:
            expected = json_load(d["data"])
            res_data = dump_to_json(d["name"], d["pk"])
            self.assertEqual(expected,res_data)
    
if __name__ == "__main__":
    unittest.main()
    
