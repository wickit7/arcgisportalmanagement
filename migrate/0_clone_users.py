# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: 0_clone_users
#
# Purpose: Script to clone users from one ArcGIS Portal to another.
#
# Author: Timo Wicki
#
# Created: 20.03.2023
# -----------------------------------------------------------------------------
import os, sys, logging, json, time
import arcpy
from arcgis.gis import GIS
from getpass import getpass
import xml.dom.minidom as DOM
from IPython.display import display
# python Skript with my own portal management functions
import portal_management_functions as pmf


def init_logging(file)  -> None:
    """Initialises logging to a file and on the console.

    Required:
        file -- The path to the log file.
    """
    global logger
    logger = logging.getLogger('myapp')
    # logging to file
    hdlr = logging.FileHandler(file, mode='w')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    # logging to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)

def search(file, text) -> int:
    """Search for a specific string in a file.

    Required:
        file -- The path to the file (e.g. log file).
        text -- The string which is to be searched for.

    Return:
        cnt -- The number of occurrences of the string in the file.
    """
    cnt = 0
    with open(file) as f:
        for line in f:
            if text in line.lower():
                cnt=cnt+1
        return cnt

def create_folder(folder_path) -> None:
    """Creates a folder if it does not already exist.

    Required:
        folder_path -- The path to the folder (e.g. log folder).
    """
    if not os.path.isdir(folder_path):
        try:
            print(f'Creating a folder: {folder_path}')
            os.makedirs(folder_path)
        except:
            raise ValueError(f'The folder "{folder_path}" does not exist and could not be created!')

if __name__ == "__main__":
    # path to a JSON input file or multiple JSON files
    paramFile = arcpy.GetParameterAsText(0)
    #paramFile = r'C:\Temp\tutorial\0_clone_users.json'

    if paramFile:        
        with open(paramFile, encoding='utf-8') as f:
            data = json.load(f)
            source_url = data["source_url"]
            target_url = data["target_url"]
            sign_in_user = data["sign_in_user"]
            clone_user_names = data["clone_user_names"]
            if "log_folder" in data:
                log_folder = data["log_folder"]
            else:
                paramFileFolder = os.path.dirname(paramFile)
                log_folder = os.path.join(paramFileFolder, "Logs") #default
    else:
        print('no Parameter-JSON file specified')
        sys.exit()
    
    ## start logging
    # create logfolder
    create_folder(log_folder)

    filename = os.path.splitext(os.path.basename(paramFile))[0]
    # path to the log file
    log_file = os.path.join(log_folder, f'{filename}.log')
    # initialise logging
    init_logging(log_file)
    logger.info(f'******************* Clone users *******************')
    logger.info(f'Start logging: {time.ctime()}')
    start_time = time.time()

    ## sign in to the portal (assume same user and pw)
    logged_in = False
    logger.info(f'Sign in to source Portal "{source_url}" and target Portal {target_url}" ')
    while logged_in == False:
        if sign_in_user:
            pw = getpass(f'Enter password for user "{sign_in_user}": ')
            try:
                source = GIS(url=source_url, username=sign_in_user, password=pw, verify_cert=False)
                target = GIS(url=target_url, username=sign_in_user, password=pw, verify_cert=False)
                logged_in = True
                logger.info(f'Successfully logged in')
                logger.info(f'Source: {source}')
                logger.info(f'Target: {target}')
            except:
                logger.info(f'Invalid password for user "{sign_in_user}". Please try again.')

    # set global parameter for portal_managment_functions.py
    pmf.ADMIN_USERNAME = sign_in_user

    # create list with users of source portal
    source_users = []
    for name in clone_user_names: 
        source_user_search = source.users.search(name)
        if source_user_search:
            # check if exactly match
            for source_user in source_user_search:
                if source_user.username == name:
                    logger.info(f"Copy user '{source_user}' from source portal" )
                    source_users.append(source_user)
                else:
                    logger.info(f"User '{source_user.username}' does not exactly match..")
        else:
            logger.error(f"User '{name}' was not found in the source portal!")

    # create list with users of target portal 
    target_usernames = [user.username for user in target.users.search('!esri_ & !admin')]
    # create enterprise users in target Portal if not already exist
    for user in source_users:
        if user.username in target_usernames:
            logger.warning(f"User '{user}' does already exist!") 
        else:
            try:
                logger.info(f"Create user '{user.username}'")
                target_user = pmf.copy_user(target, user)
                if target_user:
                    logger.info(f"Created user '{target_user.username}' in target portal")
                    #display(target_user)
                else:
                    logger.error(f'Creating user failed!') 
            except Exception:
                e = sys.exc_info()[1]
                logger.error(f'Creating user failed: {e.args[0]}')   

    ## end logging
    end_time = time.time()
    i_warning = search(log_file, "warning")
    i_error = search(log_file, "error")
    logger.info("Run Script in " + str(round(end_time - start_time)) + " sec.")
    logger.info(f'# {i_error} errors found')
    logger.info(f'# {i_warning} warnings found')
    logger.info(f'End time: {time.ctime()}')
    logger.info('****************************************************************\n')
    logger.handlers.clear()

