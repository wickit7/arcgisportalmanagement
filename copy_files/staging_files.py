# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: staging_files
#
# Purpose: Script for creating configuration files for the productive stage from
# test configuration files.
#
# Author: Timo Wicki
#
# Created: 08.10.2023
# -----------------------------------------------------------------------------
import os, sys, json

def replace_text(file_path, replace_text):
    """Search for specific strings anf replace them.

    Required:
        file_path -- The path to the file (e.g. log file).
        replace_text -- A dictionary with strings which is to be replace:

    Return:
        file with replaced text

    """
    with open(file_path, 'r') as file:
        data = file.read()
        for key in replace_text:
            value = replace_text[key]
            #print(f'Replace "{key}" with "{value}"')
            data = data.replace(key, value) # case sensitive

    return data


def write_file(data, file_path):
    if os.path.isfile(file_path):
        os.remove(file_path) # overwrite existing file
    with open(file_path, 'w') as file:
        file.write(data) 


# def create_folder(folder_path) -> None:
#     """Creates a folder if it does not already exist.

#     Required:
#         folder_path -- The path to the folder (e.g. log folder).
#     """
#     if not os.path.isdir(folder_path):
#         try:
#             print(f'Creating a folder: {folder_path}')
#             os.makedirs(folder_path)
#         except:
#             raise ValueError(f'The folder "{folder_path}" does not exist and could not be created!')

if __name__ == "__main__":
    # path to a JSON input file or multiple JSON files
    paramFile = sys.argv[1]
   
    if paramFile:        
        with open(paramFile, encoding='utf-8') as f:
            data = json.load(f)
            copy_from = data["copy_from"]
            #copy_to = data["copy_to"]
            file_types = data["file_types"]
            replace_text_filename = data["replace_text_filename"]
            replace_text_data= data["replace_text_data"]
    else:
        print('no Parameter-JSON file specified')
        sys.exit()

    # convert list to tuple
    if type(file_types) != tuple:
        file_types = tuple(file_types)

    print(f'******************* Create staging files *******************')
    # create target folder if not alread exists
    #create_folder(copy_to)
    for root, d_names, f_names in os.walk(copy_from):
        print(f'Search files in "{root}"')
        for f_name in f_names:
            if f_name.lower().endswith(file_types):
                print(f'Copy file "{f_name}"')
                input_file_path = os.path.join(root, f_name)
                out_data = replace_text(input_file_path, replace_text_data)
                out_f_name = f_name
                for key in replace_text_filename:
                    value = replace_text_filename[key]
                    out_f_name = out_f_name.replace(key, value)
                print(f'Create file "{out_f_name}"')
                write_file(out_data, os.path.join(root, out_f_name))
                               

    print('****************************************************************\n')


