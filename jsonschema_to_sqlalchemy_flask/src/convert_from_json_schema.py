#!/usr/bin/python3

import re
import argparse

from .file_handling import txt_load, json_load, txt_write

pattern = re.compile(r'(?<!^)(?=[A-Z])')

def camel_case_to_snake_case(txt):
    return pattern.sub('_', txt).lower()

def snake_case_to_camel_case(txt):
    return ''.join(word.title() for word in txt.split('_'))

def filename_without_extension(path):
    #works only for UNIX filesystems.
    return path.split("/")[-1].split(".")[0]

def get_enum_name_from_name(name):
    camel_name = snake_case_to_camel_case(name)
    return "{}Enum".format(camel_name)

def get_type(prop, snake_name):
    if prop["type"] == "string":
        if "maxLength" in prop:
            return "String({})".format(prop["maxLength"])
        if "sqlalchemytype" in prop:
            return prop["sqlalchemytype"]
        if "enum" in prop:
            return "Enum({})".format(get_enum_name_from_name(snake_name))
        return "Text"
    if prop["type"] == "number":
        if "multipleOf" in prop and prop["multipleOf"] == 1:
            return "Integer"
        return "Float"
    if prop["type"] == "boolean":
        return "Boolean"
    assert False, "Could not match type: {}".format(prop["type"])
    return ""

def is_datetime(prop):
    return prop["type"] == "string" and "sqlalchemytype" in prop and prop["sqlalchemytype"] == "DateTime"

def is_enum(prop):
    return prop["type"] == "string" and "enum" in prop

def convert_to_column(prop, snake_name, unchanged_name, model_snake_name, is_not_nullable):
    res = {
        "type":get_type(prop, snake_name),
        "snake_name": snake_name,
        "unchanged_name": unchanged_name,
        "model_snake_name": model_snake_name}
    if is_not_nullable:
        res["is_not_nullable"] = True
    if "default" in prop:
        res["default"] = {"value": prop["default"]}
    if "uniqueName" in prop and prop["uniqueName"]:
        res["unique"] = True
    if is_datetime(prop):
        res["needs_conversion_from_json"] = {
            "convert_begin": "datetime.strptime(",
            "convert_end": ",'{}')".format(prop["format"])}
        res["needs_conversion_to_json"] = {
            "convert_end": ".strftime('{}')".format(prop["format"])}
    if is_enum(prop):
        res["needs_conversion_to_json"] = {
            "convert_end": ".name"}
    return res

def convert_to_foreign_column(prop, snake_name, unchanged_name, model_snake_name, foreign_keys, is_not_nullable, lazy):
    ref = prop["$ref"]
    camel_foreign_name = snake_case_to_camel_case(filename_without_extension(ref))
    foreign_key_and_type = foreign_keys[ref]
    res = {
        "type":foreign_key_and_type[1],
        "snake_name": snake_name,
        "unchanged_name": unchanged_name,
        "model_snake_name": model_snake_name,
        "snake_foreign_key": camel_case_to_snake_case(foreign_key_and_type[0]),
        "camel_foreign_name": camel_foreign_name,
        "snake_foreign_name": camel_case_to_snake_case(filename_without_extension(ref)),
        "lazy": lazy}
    if is_not_nullable:
        res["is_not_nullable"] = True
    if "backref_name" in prop:
        res["backref"] = {"snake_own_names": prop["backref_name"]}
    return res

def is_foreign(prop):
    return "$ref" in prop

def is_unique_name(prop):
    return "uniqueName" in prop and prop["uniqueName"]

def get_foreign_names(schema):
    return [prop["$ref"] for prop in schema["properties"].values() if is_foreign(prop)]

def get_snake_unique_names(properties):
    return [camel_case_to_snake_case(prop_key) for prop_key in properties if is_unique_name(properties[prop_key])]

def get_foreign_keys(foreign_schemas):
    res = {}
    for foreign_name in foreign_schemas:
        schema = foreign_schemas[foreign_name]
        properties = schema["properties"]
        unique_names = [(prop_key,get_type(properties[prop_key], camel_case_to_snake_case(prop_key))) for prop_key in properties if is_unique_name(properties[prop_key])]
        assert len(unique_names) == 1, "Foreign files should contain exactly one unique name field!"
        res[foreign_name] = unique_names[0]
    return res
                                                              
def convert_to_model(schema, foreign_keys, camel_name, lazy):
    properties = schema["properties"]
    required = schema["required"]
    columns = []
    foreign_columns = []
    repr_list = []
    snake_name = camel_case_to_snake_case(camel_name)
    for prop_key in properties:
        prop = properties[prop_key]
        is_not_nullable = prop_key in required
        snake_prop_key = camel_case_to_snake_case(prop_key)
        if is_foreign(prop):
            foreign_columns.append(convert_to_foreign_column(prop, snake_prop_key, prop_key, snake_name, foreign_keys, is_not_nullable, lazy))
        else:
            columns.append(convert_to_column(prop, snake_prop_key, prop_key, snake_name, is_not_nullable))
        if is_unique_name(prop):
            repr_list.append(prop_key)
    
    snake_unique_names = get_snake_unique_names(properties)
    assert len(snake_unique_names) == 1, "each model must contain exactly one unique name field!"
    
    if not foreign_columns and columns:
        columns[-1]["very_last"] = True
    if foreign_columns:
        foreign_columns[-1]["very_last"] = True
    id_column = {
                    "model_snake_name":snake_name,
                    "snake_name": "id",
                    "unchanged_name": "id",
                    "type": "Integer"
                }
    res = {
        "camel_name": camel_name,
        "id_column": [id_column],
        "columns": columns,
        "foreign_columns": foreign_columns,
        "snake_name": snake_name,
        "snake_unique_name": snake_unique_names[0]
        }
    if repr_list:
        str_field = "{} ".format(camel_name) + "{}" * len(repr_list)
        format_lst = [{"value": "self.{}".format(name)} for name in repr_list]
        format_lst[0]["first"] = True
        res["repr"] = {
            "str": str_field,
            "has_format":{"format_lst": format_lst}}
    return res

def handle_enums(schema):
    properties = schema["properties"]
    enum_list = []
    for prop_key in properties:
        prop = properties[prop_key]
        if "enum" in prop:
            enum_camel_name = get_enum_name_from_name(prop_key)
            enum_list.append({
                "camel_name": enum_camel_name,
                "values": [{"unchanged_name":pair[1], "value": str(pair[0])} for pair in enumerate(prop["enum"])]
                })
    return enum_list
        
def convert_to_lines(many_line_str):
    return [{"line":line} for line in many_line_str.splitlines()]

def get_filedir(filepath):
    rs = filepath.rsplit("/",1)
    if len(rs) == 2:
        return rs[0] + "/"
    return ""

def preprocess_with_filename(filename, external=True):
    filedir = get_filedir(filename)
    def is_foreign(foreign_filename):
        return filename == filedir + foreign_filename
    return {
        "snake_name": camel_case_to_snake_case(filename_without_extension(filename)),
        "schema_data": json_load(filename, external),
        "is_foreign": is_foreign}

def get_foreign_schema(data_list_preprocessed, foreign_name):
    for data_dict in data_list_preprocessed:
        if data_dict["is_foreign"](foreign_name):
            return data_dict["schema_data"]
    
def contains_datetime(schema):
    for prop in schema["properties"].values():
        if is_datetime(prop):
            return True
    return False
    

def convert(data_list, header, middle, footer, output_flask_file, preprocess = preprocess_with_filename, lazy = True):
    enum_list = []
    model_list = []
    admin_lines = []
    data_list_preprocessed = [preprocess(date) for date in data_list]
    contains_time = False
    for data_dict in data_list_preprocessed:
        camel_name = snake_case_to_camel_case(data_dict["snake_name"])
        foreign_names = get_foreign_names(data_dict["schema_data"])
        foreign_schemas = {foreign_name: get_foreign_schema(data_list_preprocessed, foreign_name) for foreign_name in foreign_names}
        foreign_keys = get_foreign_keys(foreign_schemas)
        admin_lines.append({"camel_name":camel_name})
        model_list.append(convert_to_model(data_dict["schema_data"], foreign_keys, camel_name, lazy))
        enum_list += handle_enums(data_dict["schema_data"])
        contains_time = contains_time or contains_datetime(data_dict["schema_data"])
        
    res = {
        "header": convert_to_lines(header),
        "enums": enum_list,
        "models": model_list,
        "middle": convert_to_lines(middle),
        "admin_lines":admin_lines,
        "footer": convert_to_lines(footer),
        "contains_time": contains_time,
        "flask_file": output_flask_file
    }
    return res
    
def convert_flask_admin(data_list, output_flask_file, preprocess = preprocess_with_filename, lazy = True):
    header_filename = "templates/header.py"
    middle_filename = "templates/middle.py"
    footer_filename = "templates/footer.py"
    
    header_data = txt_load(header_filename)
    middle_data = txt_load(middle_filename)
    footer_data = txt_load(footer_filename)
    
    return convert(data_list, header_data, middle_data, footer_data, output_flask_file, preprocess, lazy)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert json schema files to preprocessed json.")
    parser.add_argument("--input_filename","-i", nargs="+", required=True, help='filenames of the json schema files.')
    parser.add_argument("--output_filename","-o", help='filename of the output file.')
    parser.add_argument("--output_flask_file","-f", help='filename without extesion of the flask output file.')

    args = parser.parse_args()
    
    output = convert_flask_admin(args.input_filename, args.output_flask_file)

    if args.output_filename is not None:
        txt_write(output, args.output_filename)
    else:
        print(output)

