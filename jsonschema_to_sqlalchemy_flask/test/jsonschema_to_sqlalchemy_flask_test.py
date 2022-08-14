#!/usr/bin/python3

import unittest
import difflib
import json

from jsonschema_to_sqlalchemy_flask.src import convert_to_sqlalchemy_flask
from jsonschema_to_sqlalchemy_flask.src import convert_to_json_loader
from jsonschema_to_sqlalchemy_flask.src import convert_to_json_dump
from jsonschema_to_sqlalchemy_flask.src import convert_to_unique_name_list_getter
from jsonschema_to_sqlalchemy_flask.src.get_order import get_order
from jsonschema_to_sqlalchemy_flask.src.file_handling import txt_load, json_load, txt_write
from jsonschema_to_sqlalchemy_flask.src.convert_from_json_schema import convert_flask_admin, filename_without_extension, preprocess_with_filename
from jsonschema_to_sqlalchemy_flask.test.helper.create_database import delete_and_recreate_database
from jsonschema_to_sqlalchemy_flask.test.expected_output.create_from_json import create_from_json
from jsonschema_to_sqlalchemy_flask.test.expected_output.dump_to_json import dump_to_json
from jsonschema_to_sqlalchemy_flask.test.expected_output.get_unique_name_list import get_unique_name_list

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
    
converted_filename = "test/expected_output/converted.json"
flask_expected_filename = "test/expected_output/result.py"
loader_expected_filename = "test/expected_output/create_from_json.py"
dump_expected_filename = "test/expected_output/dump_to_json.py"
unique_name_list_expected_filename = "test/expected_output/get_unique_name_list.py"
name_filename_unique_name_list = [
    {"name": "test2", "data": "test/data/test2.json","unique_name": "test2", "unique_name_list_name": "test2_unique_name_list"},
    {"name": "test1", "data": "test/data/test1.json","unique_name": "test1", "unique_name_list_name": "test1_unique_name_list"}] #Order is important!
unique_name_list_filename = "test/data/test_unique_name_lists.json"
schema_filename_list = ["test/data/test1.schema.json", "test/data/test2.schema.json"]


class TestJsonSchemaToSQLAlchemy(unittest.TestCase):
    def test_to_sqlalchemy_flask(self):
        self.maxDiff = None
        res_data = convert_to_sqlalchemy_flask.insert_in_template(json_load(converted_filename, False))
        expected = txt_load(flask_expected_filename)
        files_equal = check_diff(res_data, expected)
        self.assertTrue(files_equal)

    def test_to_json_loader(self):
        self.maxDiff = None
        res_data = convert_to_json_loader.insert_in_template(json_load(converted_filename, False))
        expected = txt_load(loader_expected_filename)
        files_equal = check_diff(res_data, expected)
        self.assertTrue(files_equal)
        
    def test_to_json_dump(self):
        self.maxDiff = None
        res_data = convert_to_json_dump.insert_in_template(json_load(converted_filename, False))
        expected = txt_load(dump_expected_filename)
        files_equal = check_diff(res_data, expected)
        self.assertTrue(files_equal)
        
    def test_to_unique_name_list_getter(self):
        self.maxDiff = None
        res_data = convert_to_unique_name_list_getter.insert_in_template(json_load(converted_filename, False))
        expected = txt_load(unique_name_list_expected_filename)
        files_equal = check_diff(res_data, expected)
        self.assertTrue(files_equal)
        
    def test_from_json_schema(self):
        self.maxDiff = None
        res_data = convert_flask_admin(schema_filename_list, filename_without_extension(flask_expected_filename), lambda fn: preprocess_with_filename(fn, False))
        converted = json_load(converted_filename, False)
        if converted != res_data:
            txt_write(json.dumps(res_data),"/tmp/json_schema_to_sqlalchemy_flask_res_data.json")
        self.assertEqual(converted, res_data)

    def test_get_order(self):
        res = get_order(json_load(converted_filename, False))
        self.assertEqual(res, ["test2","test1"])
        
    def test_run_test_expected(self):
        delete_and_recreate_database()
        create_from_json(name_filename_unique_name_list, lambda fn : json_load(fn, False))
        expected_unique_name_list = json_load(unique_name_list_filename, False)
        for d in name_filename_unique_name_list:
            expected = json_load(d["data"], False)
            res_data = dump_to_json(d["name"], d["unique_name"])
            self.assertEqual(expected,res_data)
            unique_name_list = get_unique_name_list(d["name"])
            self.assertEqual(expected_unique_name_list[d["unique_name_list_name"]], unique_name_list)
    
if __name__ == "__main__":
    unittest.main()
    
