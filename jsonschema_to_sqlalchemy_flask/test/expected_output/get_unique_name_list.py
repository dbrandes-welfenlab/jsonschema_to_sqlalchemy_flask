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
    parser = argparse.ArgumentParser(description="get unique names in database for the given model.")
    parser.add_argument("--modelname","-m", required=True, help='snakecase name of the model to get unique names from.')
    parser.add_argument("--output_filename","-o", help='filename of the output file.')

    args = parser.parse_args()
    
    output = get_unique_name_list(args.modelname)
    if args.output_filename is not None:
        with open(args.output_filename,"w") as output_file:
            output_file.write(json.dumps(output))
    else:
        print(output)
