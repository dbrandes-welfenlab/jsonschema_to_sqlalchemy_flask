#!/usr/bin/python3

import json
import re

pattern = re.compile(r'(?<!^)(?=[A-Z])')

def camel_case_to_snake_case(txt):
    return pattern.sub('_', txt).lower()

def snake_case_to_camel_case(txt):
    return ''.join(word.title() for word in txt.split('_'))

def filename_without_extension(path):
    #works only for UNIX filesystems.
    return path.split("/")[-1].split(".")[0]

def get_enum_name_from_name(name):
    snake_name = camel_case_to_snake_case(name)
    camel_name = snake_case_to_camel_case(snake_name)
    return "{}Enum".format(camel_name)

def get_type(prop, name):
    if prop["type"] == "string":
        if "maxLength" in prop:
            return "String({})".format(prop["maxLength"])
        if "qlalchemytype" in prop:
            return prop["qlalchemytype"]
        if "enum" in prop:
            return "Enum({})".format(get_enum_name_from_name(name))
        return "Text"
    if prop["type"] == "number":
        if "multipleOf" in prop and prop["multipleOf"] == 1:
            return "Integer"
        return "Float"
    if prop["type"] == "boolean":
        return "Boolean"
    assert False, "Could not match type: {}".format(prop["type"])
    return ""
        

def convert_to_column(prop, name, is_not_nullable):
    res = {"type":get_type(prop, name), "name": name}
    if is_not_nullable:
        res["is_not_nullable"] = True
    if "default" in prop:
        res["default"] = {"value": prop["default"]}
    return res

def convert_to_foreign_column(prop, name, is_not_nullable, lazy):
    ref = prop["$ref"]
    res = {
        "type":"Integer",
        "column_name": name,
        "foreign_key": "id",
        "foreign_name": snake_case_to_camel_case(filename_without_extension(ref)),
        "lazy": lazy,
        "small_foreign_name": camel_case_to_snake_case(filename_without_extension(ref))}
    if is_not_nullable:
        res["is_not_nullable"] = True
    if "backref_name" in prop:
        res["backref"] = {"small_own_names": prop["backref_name"]}

    return res

def in_repr(prop):
    return "showInRepr" in prop and prop["showInRepr"]

def is_foreign(prop):
    return "$ref" in prop

def convert_to_model(schema, name, create_pk, lazy):
    properties = schema["properties"]
    required = schema["required"]
    columns = []
    foreign_columns = []
    repr_list = []
    if create_pk:
        columns.append({'is_pk': True, 'name': 'id', 'type': 'Integer'})
    for prop_key in properties:
        prop = properties[prop_key]
        is_not_nullable = prop_key in required
        if is_foreign(prop):
            assert create_pk, "needs a primary key if relations are given!"
            foreign_columns.append(convert_to_foreign_column(prop, prop_key, is_not_nullable, lazy))
        else:
            columns.append(convert_to_column(prop, prop_key, is_not_nullable))
        if in_repr(prop):
            repr_list.append(prop_key)
    res = {
        "name": name,
        "columns": columns,
        "foreign_columns": foreign_columns
        }
    if repr_list:
        str_field = "{} ".format(snake_case_to_camel_case(name)) + "{}" * len(repr_list)
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
            enum_name = get_enum_name_from_name(prop_key)
            enum_list.append({
                "name": enum_name,
                "values": [{"name":pair[1], "value": str(pair[0])} for pair in enumerate(prop["enum"])]
                })
    return enum_list
        
def convert_to_lines(many_line_str):
    return [{"line":line} for line in many_line_str.splitlines()]

def convert(filename_list, header, middle, footer, create_pk = True, lazy = True):
    enum_list = []
    model_list = []
    admin_lines = []
    for filename in filename_list:
        snake_name = camel_case_to_snake_case(filename_without_extension(filename))
        camel_name = snake_case_to_camel_case(snake_name)
        
        with open(filename) as schema_file:
            data = schema_file.read()
            schema_data = json.loads(data)
        admin_lines.append({"name":camel_name})
        model_list.append(convert_to_model(schema_data, camel_name, create_pk, lazy))
        enum_list += handle_enums(schema_data)
    return {
        "header": convert_to_lines(header),
        "enums": enum_list,
        "models": model_list,
        "middle": convert_to_lines(middle),
        "admin_lines":admin_lines,
        "footer": convert_to_lines(footer)
        }
    
def convert_flask_admin(filename_list, create_pk = True, lazy = True):
    header_filename = "header.py"
    middle_filename = "middle.py"
    footer_filename = "footer.py"
    
    with open(header_filename) as header_file:
        header_data = header_file.read()
    
    with open(middle_filename) as middle_file:
        middle_data = middle_file.read()
    
    with open(footer_filename) as footer_file:
        footer_data = footer_file.read()
    
    return convert(filename_list, header_data, middle_data, footer_data, create_pk, lazy)

        
