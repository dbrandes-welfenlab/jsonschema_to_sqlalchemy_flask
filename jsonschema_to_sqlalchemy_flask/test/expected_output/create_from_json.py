#!/usr/bin/python3

from .result import db, Test1, Test2
import json
import argparse

from datetime import datetime

def add_test1(json_data):
    test1 = Test1(
        str_field_fixed_length_as_unique_name = json_data["str_field_fixed_length_as_unique_name"],
        txt_field = json_data["txt_field"],
        date_field_now = datetime.strptime(json_data["date_field_now"],'%d.%m.%y %H:%M:%S'),
        int_field = json_data["int_field"],
        bool_field = json_data["bool_field"],
        float_field = json_data["float_field"],
        enum_field = json_data["enum_field"],
        test2_name = json_data["test2_name"]
        )
    
    db.session.add(test1)
    db.session.commit()

def add_test2(json_data):
    test2 = Test2(
        name = json_data["name"]
        )
    
    db.session.add(test2)
    db.session.commit()

def create_from_json(name_data_dict_list, preprocess = lambda x:x):
    for name_data_dict in name_data_dict_list:
        if name_data_dict["name"] == "test1":
            add_test1(preprocess(name_data_dict["data"]))
        if name_data_dict["name"] == "test2":
            add_test2(preprocess(name_data_dict["data"]))

def json_load(filename):
    with open(filename) as filehandle:
        return json.load(filehandle)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fill data in database from a json file.")
    parser.add_argument("--input_filename","-i", required=True, nargs='+', help='filenames of the input json files.')
    parser.add_argument("--modelname","-m", required=True, nargs='+', help='snakecase names of the models to be filled with data.')

    args = parser.parse_args()
    
    name_data_dict_list = [{"name":name, "data": filename} for (name,filename) in zip(args.modelname,args.input_filename)]
    create_from_json(name_data_dict_list,json_load)
