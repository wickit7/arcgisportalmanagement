# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: 3_clone_items
#
# Purpose: Script to clone items from one ArcGIS Portal to another.
#
# Author: Timo Wicki
#
# Created: 20.03.2023
# -----------------------------------------------------------------------------
import os, sys, logging, json, time
import arcpy
from arcgis.gis import GIS
from getpass import getpass
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
    #paramFile = r'C:\Temp\tutorial\3_clone_items.json'

    if paramFile:        
        with open(paramFile, encoding='utf-8') as f:
            data = json.load(f)
            source_url = data["source_url"]
            target_url = data["target_url"]
            sign_in_user = data["sign_in_user"]
            if "replace_urls" in data:
                replace_urls = data["replace_urls"]
            else:
                replace_urls = None  #default
            clone_source_items = data["clone_source_items"]                
            if "log_folder" in data:
                log_folder = data["log_folder"]
            else:
                paramFileFolder = os.path.dirname(paramFile)
                log_folder = os.path.join(paramFileFolder, "Logs") #default
            use_org_basemap = True  #default
            # if depreciated parameter is used (now "use_org_basemap" should be used in dictionary "clone_source_items")
            if "use_org_basemap" in data:
                if data["use_org_basemap"] == "False":
                    use_org_basemap = False
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
    logger.info(f'******************* Clone items *******************')
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
    pmf.SIGN_IN_USERNAME = sign_in_user

    ## get item mapping
    # dictionary to map source ids with target ids
    source_target_itemId_map = {}
    # dictionary to store the item mapping for all source items to be cloned
    source_target_item_mapping = {}
    # clone all source items
    for clone_source_item in clone_source_items:
        # source Item mit ID abrufen
        try:
            source_item = source.content.get(clone_source_item['item_id'])  
            logger.info(f"Copy source item '{source_item.title}' ('{source_item.id}') of type '{source_item.type}'")
        except:
            logger.error(f"Source Item '{clone_source_item['item_id']}' was not found!'")        
            continue

        # check if item already exists in the targt portal
        found_target_item = pmf.get_target_item(target, source_item, replace_urls)

        if found_target_item:
            logger.warning(f"Item with the titel '{found_target_item.title}' already exists (target ID: '{found_target_item.id}') and ist not created again!\n")
            continue                           

        # create item mapping based on titel (and url)                                  
        item_mapping = {}
        # start key
        item_mapping_source_items = [source_item]
        # rekursiv alle abhängigen Items hinzufügen 
        logger.info(f'Creating item mapping')
        while item_mapping_source_items:
            # item mapping for a list of source items (current recursion level)
            try:
                item_mapping_level = pmf.get_item_mapping(source, target, item_mapping_source_items, source_target_itemId_map, replace_urls)
            except Exception:
                    e = sys.exc_info()[1]
                    logger.error(f'Creating item mapping failed: {e.args[0]}')
                    raise           
            item_mapping_source_items = []
            # extend item_mapping, update item_mapping_source_items
            if item_mapping_level:
                for source_item_id in item_mapping_level.keys():
                    if source_item_id not in item_mapping:
                        item_mapping[source_item_id] = item_mapping_level[source_item_id]
                    if  source_item_id in source_target_item_mapping.keys():
                        # if the item_mapping for an item already exists, do not search again
                        logger.info(f"Item mapping already exists for '{source_item_id}'")
                        item_mapping.update(source_target_item_mapping[source_item_id])
                    else:
                        # if item_mapping does not yet exist, it must still be created
                        item_mapping_source_items.append(source.content.get(source_item_id))                                                          

        # get input parameters for clone_items
        folder = None #default
        if 'folder' in clone_source_item:
            folder = clone_source_item['folder']
        preserve_item_id = False #default
        if 'preserve_item_id' in clone_source_item:
            if clone_source_item['preserve_item_id'] == "True":
                preserve_item_id = True
        item_extent = None #default
        if 'item_extent' in clone_source_item:
            item_extent = clone_source_item['item_extent']
        if 'use_org_basemap' in clone_source_item: # default = True
            if clone_source_item['use_org_basemap'] == "False":
                use_org_basemap = False
        copy_data = True #default
        if 'copy_data' in clone_source_item:
            if clone_source_item['copy_data'] == "False":
                copy_data = False      
        copy_global_ids = False #default
        if 'copy_global_ids' in clone_source_item:
            if clone_source_item['copy_global_ids'] == "True":
                copy_global_ids = True
        search_existing_items = True #default   
        if 'search_existing_items' in clone_source_item:
            if clone_source_item['search_existing_items'] == "False":
                search_existing_items = False
        # get owner form source portal
        owner = source_item.owner
        # if item is hosted, parameters for the clone_items function have to be adjusted
        if pmf.is_hosted(source_item):
            logger.info("Service ist gehosted")
            copy_data = True 
            copy_global_ids = True

        logger.info(f"Parameters for clone_items: ")
        logger.info(f"- source_item: {source_item}")
        logger.info(f"- folder: {folder}")
        logger.info(f"- item_extent: {item_extent}")
        logger.info(f"- use_org_basemap: {use_org_basemap}")
        logger.info(f"- copy_data: {copy_data}") 
        logger.info(f"- copy_global_ids: {copy_global_ids}")  
        logger.info(f"- search_existing_items: {search_existing_items}")                                  
        logger.info(f"- item_mapping: {item_mapping}")
        logger.info(f"- owner: {owner}")
        logger.info(f"- preserve_item_id: {preserve_item_id}")
        
        try:
            logger.info(f"Start cloning item")
            target_items = target.content.clone_items(
                                items=[source_item], folder=folder, item_extent=item_extent,
                                use_org_basemap=use_org_basemap, copy_data=copy_data, copy_global_ids=copy_global_ids, 
                                search_existing_items=search_existing_items, item_mapping=item_mapping, owner=owner,
                                preserve_item_id=preserve_item_id)
        except Exception:
                e = sys.exc_info()[1]
                logger.error(f'Cloning item failed: {e.args[0]}')
                raise

        if item_mapping:
            # update dictionaries
            source_target_item_mapping[source_item.id] = item_mapping  
            source_target_itemId_map.update(item_mapping)
        
        if len(target_items)>1:
            logger.info(f"When trying to clone the item '{source_item.title}' more than one item was cloned!")
        
        for target_item in target_items:
            logger.info(f"Created target Item '{target_item.title}' ('{target_item.id}')")
            # update dictionary with source Id and target Id
            if target_item.title == source_item.title and target_item.type == source_item.type:
                source_target_itemId_map[source_item.id] = target_item.id
            else:
                source_items_search = source.content.search(query=f'title: "{target_item.title}"', item_type=target_item.type)
                if source_items_search:
                    # check if wheter there is an exact match 
                    for source_item_s in source_items_search:
                        if source_item_s.title == target_item.title:
                            source_target_itemId_map[source_item_s.id] = target_item.id
                
            # update url of dependent url elements
            #fd_items = target_item.dependent_upon()
            #if fd_items['total'] > 0:
            #    for fd_item in fd_items['list']:
            #        if fd_item['dependencyType'] == 'url':
            #            # check whether a mapping has been specified in the JSON for the item.
            #            if 'url_mapping' in clone_source_item.keys():
            #                if fd_item['url'] in clone_source_item['url_mapping']:
            #                    print(f"Replace url '{fd_item['url']}' with '{clone_source_item['url_mapping'][fd_item['url']]}'") 
            #                    # update url-Item
            #                    fd_item.update({"url":clone_source_item['url_mapping'][fd_item['url']]}) # ******* target_item is not updated !??
            #            else:
            #                 # check if the url contains characters that appear in replace_urls.keys
            #                for key in replace_urls.keys():
            #                    if key in fd_item['url']: 
            #                        print(f"Replace '{key}' with '{replace_urls[key]}'")
            #                        # update url-Item
            #                        fd_item.update({"url":fd_item['url'].replace(key, replace_urls[key])}) # ******* target_item is not updated !??
                                    
                                
        # Get group membership from source Portal -> alternatively use parameter 'group_mapping' in 'clone_items'
        logger.info("Share target Item")
        share_options = source_item.shared_with
        target_groups = []
        for source_group in share_options['groups']:
            target_group_search = target.groups.search(f"title: {source_group.title}")
            if target_group_search:
                # check whether there is an exact match
                for target_group in target_group_search:
                    if target_group.title == source_group.title:
                        logger.info(f"Add item to group '{target_group.title}'")
                        target_groups.append(target_group)
                    else:
                        logger.info(f"Group '{target_group.title}' does not exactly match with the 'Title'..")
            else:
                logger.error(f"Group '{source_group.title}' was not found in the target portal!")
                
        # share target item
        logger.info(f"Parameters for share item: ")
        everyone = share_options['everyone']
        org = share_options['org']
        logger.info(f"- everyone: {everyone}")
        logger.info(f"- organisation: {org}")
        logger.info(f"- groups: {target_groups}")

        for target_item in target_items:
            if target_groups:
                target_item.share(everyone=everyone, org=org, groups=target_groups)
            else:
                target_item.share(everyone=everyone, org=org)

            logger.info("Shared target Item")
            #display(target_item)
                               
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

