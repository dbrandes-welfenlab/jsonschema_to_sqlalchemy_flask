#!/usr/bin/python3

from .result import db, Test1, Test2
import json
import argparse

from datetime import datetime

def add_test1(json_data):
    #test2 = Test2.query.filter_by(name=json_data["test2_name"]).first()
    #assert(test2 is not None)
    test1 = Test1(
        str_field_fixed_length_as_pk = json_data["str_field_fixed_length_as_pk"],
        txt_field = json_data["txt_field"],
        date_field_now = datetime.strptime(json_data["date_field_now"],"%d.%m.%y %H:%M:%S"),
        int_field = json_data["int_field"],
        bool_field = json_data["bool_field"],
        float_field = json_data["float_field"],
        enum_field = str(json_data["enum_field"]),
        test2_name = json_data["test2_name"])
    
    db.session.add(test1)
    db.session.commit()

def add_test2(json_data):
    test2 = Test2(name=json_data["name"])
    
    db.session.add(test2)
    db.session.commit()

def create_from_json(name_data_dict_list,preprocess=lambda x:x):
    for d in name_data_dict_list:
        if d["name"] == "test1":
            add_test1(preprocess(d["data"]))
        if d["name"] == "test2":
            add_test2(preprocess(d["data"]))
                
if __name__ == "__main__":
    pass
    #parser = argparse.Parser()
    #parser.add_
