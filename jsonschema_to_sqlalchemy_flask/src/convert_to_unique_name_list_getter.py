#!/usr/bin/python3

import argparse

from .file_handling import txt_load, json_load, txt_write

template_filename = "templates/get_unique_name_list_template.mustache"

from chevron.renderer import render

def insert_in_template(converted_data):
    template_data = txt_load(template_filename)
    return render(template=template_data, data=converted_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert preprocessed json to unique name list getter python code.")
    parser.add_argument("--input_filename","-i", required=True, help='filename of the preprocessed json file.')
    parser.add_argument("--output_filename","-o", help='filename of the output file.')

    args = parser.parse_args()
    
    output = insert_in_template(json_load(args.input_filename))
    if args.output_filename is not None:
        txt_write(output, args.output_filename)
    else:
        print(output)

