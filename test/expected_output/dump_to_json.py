#!/usr/bin/python3

from .result import db, Test1, Test2
import json
import argparse

def dump_test1(unique_name):
    test1 = Test1.query.filter_by(str_field_fixed_length_as_unique_name=unique_name).first()
    assert(test1 is not None)
    res = {}
    res["str_field_fixed_length_as_unique_name"] = test1.str_field_fixed_length_as_unique_name
    res["txt_field"] = test1.txt_field
    res["date_field_now"] = test1.date_field_now.strftime('%d.%m.%y %H:%M:%S')
    res["int_field"] = test1.int_field
    res["bool_field"] = test1.bool_field
    res["float_field"] = test1.float_field
    res["enum_field"] = test1.enum_field.name
    res["test2_name"] = test1.test2_name
    return res

def dump_test2(unique_name):
    test2 = Test2.query.filter_by(name=unique_name).first()
    assert(test2 is not None)
    res = {}
    res["name"] = test2.name
    return res

def dump_to_json(name, unique_name):
    if name == "test1":
        return dump_test1(unique_name)
    if name == "test2":
        return dump_test2(unique_name)

if __name__ == "__main__":
    pass
    

