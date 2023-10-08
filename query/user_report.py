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
import os, sys, logging, json, time, datetime
import arcpy
from arcgis.gis import GIS
from getpass import getpass
from IPython.display import display
# python Skript with my own portal management functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'migrate'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Migrate', 'Portal'))
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

    if paramFile:        
        with open(paramFile, encoding='utf-8') as f:
            data = json.load(f)
            target_url = data["target_url"]
            sign_in_user = data["sign_in_user"]
            user_name = data["user_name"]
            if "log_folder" in data:
                log_folder = data["log_folder"]
            else:
                paramFileFolder = os.path.dirname(paramFile)
                log_folder = os.path.join(paramFileFolder, "Logs") #default
            if "report_folder" in data:
                report_folder = data["report_folder"]
            else:
                paramFileFolder = os.path.dirname(paramFile)
                report_folder = os.path.join(paramFileFolder, "Reports") #default
    else:
        print('no Parameter-JSON file specified')
        sys.exit()
    
    ## start logging
    # create logfolder and reportfolder
    create_folder(report_folder)
    create_folder(log_folder)

    filename = os.path.splitext(os.path.basename(paramFile))[0]
    # path to the log file
    log_file = os.path.join(log_folder, f'{filename}.log')
    # initialise logging
    init_logging(log_file)
    logger.info(f'******************* User reports *******************')
    logger.info(f'Start logging: {time.ctime()}')
    start_time = time.time()

    # report_file
    report_file = os.path.join(report_folder, f'{filename}.txt')
    if os.path.exists(report_file):
        os.remove(report_file)

    ## sign in to the portal (assume same user and pw)
    logged_in = False
    logger.info(f'Sign in to target Portal {target_url}" ')
    while logged_in == False:
        if sign_in_user:
            pw = getpass(f'Enter password for user "{sign_in_user}": ')
            try:
                target = GIS(url=target_url, username=sign_in_user, password=pw, verify_cert=False)
                logged_in = True
                logger.info(f'Successfully logged in')
            except:
                logger.info(f'Invalid password for user "{sign_in_user}". Please try again.')

    # set global parameter for portal_managment_functions.py
    pmf.ADMIN_USERNAME = sign_in_user


    # create list with users of source portal
    search_users = target.users.search(user_name)
    with open(report_file, 'a') as file:
        if search_users:
            for user in search_users:
                # Log user information
                logger.info(f'Report user "{user}"')
                file.write(f'\n*************** User report "{user.username}" ***************\n')
                file.write(f'\n****General informations ****\n')
                file.write(f"Full Name: {user.fullName}\n")
                file.write(f"Email: {user.email}\n")
                file.write(f"User ID: {user.id}\n")
                # Convert created and lastLogin timestamps to datetime objects
                created_timestamp = datetime.datetime.fromtimestamp(user.created / 1000)
                last_login_timestamp = datetime.datetime.fromtimestamp(user.lastLogin / 1000)
                file.write(f"Created: {created_timestamp.strftime('%d-%m-%Y %H:%M:%S')}\n")
                file.write(f"Last Login: {last_login_timestamp.strftime('%d-%m-%Y %H:%M:%S')}\n")
                file.write(f"Role: {user.role}\n")
                file.write(f"Level: {user.level}\n")
                file.write(f"User License Type: {user.userLicenseTypeId}\n")

                file.write(f'\n****Items Owned by the User ****\n')
                # Get all items owned by the user
                user_items_root = user.items() # root?
                    # Log and return the items
                file.write(f"# Root Folder\n")
                for item in user_items_root:
                    file.write(f"Item ID: {item.id}\n")
                    file.write(f"Item Name: {item.title}\n")
                    file.write(f"Item Type: {item.type}\n")
                    file.write(f"Item URL: {item.url}\n\n")
                folders = user.folders
                for folder in folders:
                    file.write(f"# Folder '{folder['title']}'\n")
                    items = user.items(folder=folder["title"])
                    for item in items:
                        file.write(f"Item ID: {item.id}\n")
                        file.write(f"Item Name: {item.title}\n")
                        file.write(f"Item Type: {item.type}\n")
                        file.write(f"Item URL: {item.url}\n\n")
                            
                # Get all groups the user belongs to
                user_groups = user.groups
                file.write(f'****Groups the user belongs to****\n')
                user_groups = user.groups
                for group in user_groups:
                    file.write(f"Group ID: {group.id}\n")
                    file.write(f"Group Name: {group.title}\n")
                    file.write(f"Group Owner: {group.owner}\n")
                    file.write(f"Group Access: {group.access}\n\n")

                file.write(f'*************** End user reports ***************\n')
        else:
            logger.error(f"User '{user_name}' was not found in the target portal!")

    ## end logging
    end_time = time.time()
    i_warning = search(report_file, "warning")
    i_error = search(report_file, "error")
    logger.info("Run Script in " + str(round(end_time - start_time)) + " sec.")
    logger.info(f'# {i_error} errors found')
    logger.info(f'# {i_warning} warnings found')
    logger.info(f'End time: {time.ctime()}')
    logger.info('****************************************************************\n')
    logger.handlers.clear()

