import unittest
from difflib import Differ

from src.convert_to_sqlalchemy_flask import insert_from_file
from src.convert_from_json_schema import convert_flask_admin

import json
import yaml

def check_equal(difference):
    equal = True
    for line in difference:
        if not line.startswith("  "):
            equal = False
    return equal

def check_diff(txt1, txt2):
    d = Differ()
    difference = d.compare(txt1.split("\n"), txt2.split("\n"))
    if check_equal(difference):
        return True
    for line in difference:
         print (line)
    return False
         
filename_list = ["test/test1.schema.json", "test/test2.schema.json"]
converted_filename = "test/converted.json"
expected_result_filename = "test/result.py"
         
class TestFromJsonSchema(unittest.TestCase):
    def test_convert(self):
        self.maxDiff = None
        calculated_converted_data = convert_flask_admin(filename_list)
        
        with open(converted_filename) as converted_file:
            readed_converted_data = json.loads(converted_file.read())
            
        self.assertEqual(calculated_converted_data,readed_converted_data)
        
class TestToSQLAlechemyFlask(unittest.TestCase):
    def test_convert(self):
        with open(expected_result_filename) as expected_result_file:
            expected_result = expected_result_file.read()

        result = insert_from_file(converted_filename)
        
        self.assertTrue(check_diff(result, expected_result))
        

if __name__ == "__main__":
    unittest.main()

