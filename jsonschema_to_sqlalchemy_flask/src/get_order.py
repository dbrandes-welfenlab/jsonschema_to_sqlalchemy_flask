#!/usr/bin/python3

import argparse

from .file_handling import json_load, txt_write

def deep_search(node):
    #parents must be created first, then child nodes, so parents get lower number.
    order_num = node["order_num"]
    for child in node["childs"]:
        if not "order_num" in child or child["order_num"] <= order_num:
            child["order_num"] = order_num + 1
            deep_search(child)
    for parent in node["parents"]:
        if not "order_num" in parent or parent["order_num"] >= order_num:
            parent["order_num"] = order_num - 1
            deep_search(parent)
            
def handle_all_nodes(node_list):
    while [True for node in node_list if "order_num" not in node]:
        node = [node for node in node_list if "order_num" not in node][0]
        node["order_num"] = 0
        deep_search(node)
        
def offset_all_nodes(node_list):
    minimum = min([node["order_num"] for node in node_list])
    for node in node_list:
        node["order_num"] -= minimum

def get_order(converted_data):
    #create node dicts:
    node_list = [{"camel_name": model["camel_name"], "snake_name": model["snake_name"], "parents": [foreign_column["camel_foreign_name"] for foreign_column in model["foreign_columns"]], "childs":[]} for model in converted_data["models"]]
    #replace parent name with parent node:
    for node in node_list:
        for i,camel_parent_name in enumerate(node["parents"]):
            for node_inner in node_list:
                if camel_parent_name == node_inner["camel_name"]:
                    node["parents"][i] = node_inner
    
    #add child nodes:
    for node in node_list:
        for parent in node["parents"]:
            parent["childs"].append(node)
            
    #traversal and set numbers (start with zero at the first (until all nodes are visited)):
    handle_all_nodes(node_list)
    #offset nodes (order_num should start with zero):
    offset_all_nodes(node_list)
    #create order:
    node_list.sort(key = lambda node: node["order_num"])
    order_name = [node["snake_name"] for node in node_list]
    return order_name

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="get order for adding input data.")
    parser.add_argument("--input_filename","-i", required=True, help='filename of the preprocessed json file.')
    parser.add_argument("--output_filename","-o", help='filename of the output file.')

    args = parser.parse_args()
    
    output = get_order(json_load(args.input_filename))
    if args.output_filename is not None:
        txt_write(output, args.output_filename)
    else:
        print(output)

