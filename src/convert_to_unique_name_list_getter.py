import sys
import json
import argparse

template_filename = "templates/get_unique_name_list_template.mustache"

from chevron.renderer import render

def insert_in_template(converted_data):
    with open(template_filename) as template_file:
        template_data = template_file.read()
    return render(template=template_data, data=converted_data)

def read_json(filename):
    with open(filename) as filehandle:
        return json.load(filehandle)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert preprocessed json to unique name list getter python code.")
    parser.add_argument("--input_filename","-i", required=True, help='filename of the preprocessed json file.')
    parser.add_argument("--output_filename","-o", help='filename of the output file.')

    args = parser.parse_args()
    
    output = insert_in_template(read_json(args.input_filename))
    if args.output_filename is not None:
        with open(args.output_filename,"w") as output_file:
            output_file.write(output)
    else:
        print(output)

