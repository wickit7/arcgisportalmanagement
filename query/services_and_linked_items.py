# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: services_and_linked_items
#
# Purpose: Script to list all services and items that use them, of each hosted and federated sever.
#
# Author: Timo Wicki
#
# Created: 13.11.2023
# -----------------------------------------------------------------------------
import os, sys, logging, json, time, datetime
import arcpy
from arcgis.gis import GIS
from getpass import getpass
from IPython.display import display
from arcgis.mapping import WebMap
from arcgis.mapping import WebScene

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
            portal_url = data["portal_url"]
            sign_in_user = data["sign_in_user"]
            if "replace_urls" in data:
                replace_urls = data["replace_urls"]
            else:
                replace_urls = {}           
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
    report_file_wm = os.path.join(report_folder, 'webMapsReferences.json')
    if os.path.exists(report_file_wm):
        os.remove(report_file_wm)
    report_file_ws = os.path.join(report_folder, 'webScenesReferences.json')
    if os.path.exists(report_file_ws):
        os.remove(report_file_ws)
    report_file_services = os.path.join(report_folder, 'servicesReferences.json')
    if os.path.exists(report_file_services):
        os.remove(report_file_services)

    ## sign in to the portal (assume same user and pw)
    logged_in = False
    logger.info(f'Sign in to target Portal {portal_url}" ')
    while logged_in == False:
        if sign_in_user:
            pw = getpass(f'Enter password for user "{sign_in_user}": ')
            try:
                gis = GIS(url=portal_url, username=sign_in_user, password=pw, verify_cert=False)
                logged_in = True
                logger.info(f'Successfully logged in')
            except:
                logger.info(f'Invalid password for user "{sign_in_user}". Please try again.')

    # set global parameter for portal_managment_functions.py
    pmf.ADMIN_USERNAME = sign_in_user

    # Get all web map items and build a dictionary of references
    web_map_references = {}
    for ii, item in enumerate(gis.content.search(query='* AND type:"Web Map"', max_items=1000)):  # Increase max_items if needed
        print(f"{ii}: web map item '{item.title}'")
        webmap_obj = WebMap(item)
        web_map_references[item.id] = {
            "title": item.title,
            "itemid": item.itemid ,
            "type": item.type,
            "homepage": item.homepage,
            "dependencies": dict(item.dependencies.properties)['items']
            } 
        web_map_references[item.id]["baseMapLayers"] = [] 
        for layer in webmap_obj.basemap.baseMapLayers:
            layer_info = {
                "id": layer['id'],
                "title": layer['title'],
                "layerType": layer['layerType']
            }
            if hasattr(layer, 'itemId'):
                layer_info["itemId"] = layer['itemId']
            if hasattr(layer, 'url'):
                layer_info["url"] = layer['url']
            web_map_references[item.id]["baseMapLayers"].append(layer_info)
        web_map_references[item.id]["layers"] = [] 
        for layer in webmap_obj.layers:
            layer_info = {
                "id": layer['id'],
                "title": layer['title'],
                "layerType": layer['layerType']
            }
            if hasattr(layer, 'itemId'):
                layer_info["itemId"] = layer['itemId']
            if hasattr(layer, 'url'):
                layer_info["url"] = layer['url']
            web_map_references[item.id]["layers"].append(layer_info)
            

    web_scene_references = {}
    for ii, item in enumerate(gis.content.search(query='* AND type:"Web Scene"', max_items=1000)):  # Increase max_items if needed
        print(f"{ii}: web scence item '{item.title}'")
        webscene_obj = WebScene(item)
        web_scene_references[item.id] = {
            "title": item.title,
            "itemid": item.itemid ,
            "type": item.type,
            "homepage": item.homepage,
            "dependencies": dict(item.dependencies.properties)['items']
            } 
        web_scene_references[item.id]["baseMapLayers"] = [] 
        for layer in webscene_obj['baseMap']['baseMapLayers']:
            layer_info = {
                "id": layer['id'],
                "title": layer['title'],
                "layerType": layer['layerType']
            }
            try:
                layer_info["itemId"] = layer['itemId']
            except:
                print('')
            try:
                layer_info["url"] = layer['url']
            except:
                print('')
            web_scene_references[item.id]["baseMapLayers"].append(layer_info)

        web_scene_references[item.id]["groundLayers"] = [] 
        for layer in webscene_obj['ground']['layers']:
            layer_info = {
                "id": layer['id'],
                "title": layer['title'],
                "layerType": layer['layerType']
            }
            try:
                layer_info["itemId"] = layer['itemId']
            except:
                print('')
            try:
                layer_info["url"] = layer['url']
            except:
                print('')
            web_scene_references[item.id]["groundLayers"].append(layer_info)
        web_scene_references[item.id]["operationalLayers"] = [] 
        for layer in webscene_obj['operationalLayers']:
            layer_info = {
                "id": layer['id'],
                "title": layer['title'],
                "layerType": layer['layerType']
            }
            try:
                layer_info["itemId"] = layer['itemId']
            except:
                print('')
            try:
                layer_info["url"] = layer['url']
            except:
                print('')
            web_scene_references[item.id]["operationalLayers"].append(layer_info)

    # create dictionary with all relevant data
    report_data = {}
    # create list with users of source portal
    gis_servers = gis.admin.servers.list()
    for server in gis_servers:
        # Log user information
        logger.info(f'Services server "{server}"')
        # list all services
        services = server.services.list()
        server_folders = server.services.folders
        for server_folder in server_folders:
            services.extend(server.services.list(folder = server_folder))
            
        for ii, service in enumerate(services):
            print(f"{ii}: web map item '{service.url}'")
            web_url = service.url
            for key in replace_urls:
                web_url = web_url.replace(key, replace_urls[key])
            # replace ".type" to "/type"
            url_end = web_url.split(r"/")[-1]
            web_url = web_url.replace (url_end, url_end.replace(".", r"/"))
            report_data[service.url] = {
                'web_url': web_url,
                'serviceName': service.properties.serviceName,
                'type': service.properties.type,
                'private': service.properties.private
            }

            # Check if portalItems is available before adding it
            if hasattr(service.properties, 'portalProperties'):
                if hasattr(service.properties.portalProperties, 'portalItems'):
                    # check references for each portal Item
                    portal_items = []
                    for ii, item in enumerate(service.properties.portalProperties.portalItems):
                        portal_item = {
                            "itemID": item.itemID,
                            "type": item.type,
                        }
                        # search for web maps that use the service
                        consuming_wm = []
                        for ref in web_map_references:
                            for layer in web_map_references[ref]['layers']:
                                if isinstance(layer, dict) and 'itemId' in layer:
                                    if layer['itemId'] == item.itemID:
                                        layer_info = {
                                            "LayerId": layer.get('id'),
                                            "LayerTitle": layer.get('title'),
                                            "layerType": layer.get('layerType'),
                                            "layerItemId": layer.get('itemId'),
                                            "webMapId": web_map_references[ref].get('itemid'),
                                            "webMapTitle": web_map_references[ref].get('title'),
                                            "webMapType": web_map_references[ref].get('type'),
                                            "webMapHomepage": web_map_references[ref].get('homepage')
                                        }
                                        if 'url' in layer:
                                            layer_info['LayerUrl'] = layer['url']
                                        consuming_wm.append(layer_info)
                            for layer in web_map_references[ref]['baseMapLayers']:
                                if isinstance(layer, dict) and 'itemId' in layer:
                                    if layer['itemId'] == item.itemID:
                                        layer_info = {
                                            "LayerId": layer.get('id'),
                                            "LayerTitle": layer.get('title'),
                                            "layerType": layer.get('layerType'),
                                            "layerItemId": layer.get('itemId'),
                                            "webMapId": web_map_references[ref].get('itemid'),
                                            "webMapTitle": web_map_references[ref].get('title'),
                                            "webMapType": web_map_references[ref].get('type'),
                                            "webMapHomepage": web_map_references[ref].get('homepage')
                                        }
                                        if 'url' in layer:
                                            layer_info['LayerUrl'] = layer['url']
                                        consuming_wm.append(layer_info)
                        if consuming_wm:                        
                            portal_item['webMaps'] = list(consuming_wm)
                        # search for web scenes that use the service
                        consuming_ws = []
                        for ref in web_scene_references:
                            for layer in web_scene_references[ref]['operationalLayers']:
                                if isinstance(layer, dict) and 'itemId' in layer:
                                    if layer['itemId'] == item.itemID:
                                        layer_info = {
                                            "LayerId": layer.get('id'),
                                            "LayerTitle": layer.get('title'),
                                            "layerType": layer.get('layerType'),
                                            "layerItemId": layer.get('itemId'),
                                            "webSceneId": web_scene_references[ref].get('itemid'),
                                            "webSceneTitle": web_scene_references[ref].get('title'),
                                            "webSceneType": web_scene_references[ref].get('type'),
                                            "webSceneHomepage": web_scene_references[ref].get('homepage')
                                        }
                                        if 'url' in layer:
                                            layer_info['LayerUrl'] = layer['url']
                                        consuming_ws.append(layer_info)
                            for layer in web_scene_references[ref]['groundLayers']:
                                if isinstance(layer, dict) and 'itemId' in layer:
                                    if layer['itemId'] == item.itemID:
                                        layer_info = {
                                            "LayerId": layer.get('id'),
                                            "LayerTitle": layer.get('title'),
                                            "layerType": layer.get('layerType'),
                                            "webSceneId": web_scene_references[ref].get('itemid'),
                                            "webSceneTitle": web_scene_references[ref].get('title'),
                                            "webSceneType": web_scene_references[ref].get('type'),
                                            "webSceneHomepage": web_scene_references[ref].get('homepage')
                                        }
                                        if 'url' in layer:
                                            layer_info['LayerUrl'] = layer['url']
                                        consuming_ws.append(layer_info)

                            for layer in web_scene_references[ref]['baseMapLayers']:
                                if isinstance(layer, dict) and 'itemId' in layer:
                                    if layer['itemId'] == item.itemID:
                                        layer_info = {
                                            "LayerId": layer.get('id'),
                                            "LayerTitle": layer.get('title'),
                                            "layerType": layer.get('layerType'),
                                            "layerItemId": layer.get('itemId'),
                                            "webMapId": web_map_references[ref].get('itemid'),
                                            "webMapTitle": web_map_references[ref].get('title'),
                                            "webMapType": web_map_references[ref].get('type'),
                                            "webMapHomepage": web_map_references[ref].get('homepage')
                                        }
                                        if 'url' in layer:
                                            layer_info['LayerUrl'] = layer['url']
                                        consuming_ws.append(layer_info)
                        if consuming_ws:                        
                            portal_item['webScenes'] = list(consuming_ws)
                        portal_items.append(portal_item) 
                    if portal_items:
                        report_data[service.url]['portalItems'] = list(portal_items)
                    if hasattr(service.properties.portalProperties, 'isHosted'):
                        report_data[service.url]['isHosted'] = service.properties.portalProperties.isHosted

    # write json to file
    with open(report_file_wm, 'w') as json_file:
        json.dump(web_map_references, json_file, indent=2, ensure_ascii=False).encode('utf8')
    with open(report_file_ws, 'w') as json_file:
        json.dump(web_scene_references, json_file, indent=2, ensure_ascii=False).encode('utf8')
    with open(report_file_services, 'w') as json_file:
        json.dump(report_data, json_file, indent=2, ensure_ascii=False).encode('utf8')

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

