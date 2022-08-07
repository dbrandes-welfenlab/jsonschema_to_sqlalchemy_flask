#!/usr/bin/python3

from .result import db, Test1, Test2
import json
import argparse

def get_unique_name_list_test1():
    return [test1.str_field_fixed_length_as_unique_name for test1 in Test1.query]

def get_unique_name_list_test2():
    return [test2.name for test2 in Test2.query]

def get_unique_name_list(name):
    if name == "test1":
        return get_unique_name_list_test1()
    if name == "test2":
        return get_unique_name_list_test2()

if __name__ == "__main__":
    pass
    

