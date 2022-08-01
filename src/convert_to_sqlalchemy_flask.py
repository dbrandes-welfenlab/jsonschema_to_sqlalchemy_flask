import sys
import json

template_filename = "template.mustache"

from chevron.renderer import render

def insert_in_template(converted_data):
    with open(template_filename) as template_file:
        template_data = template_file.read()
        return render(template=template_data, data=converted_data)

def insert_from_file(converted_filename):
    with open(converted_filename) as converted_file:
        converted_data = json.loads(converted_file.read())
        return insert_in_template(converted_data)

if __name__ == "__main__":
    converted_filename = sys.argv[1]
    print(insert_from_file(converted_filename))

