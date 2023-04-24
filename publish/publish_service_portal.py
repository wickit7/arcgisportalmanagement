# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: publish_service_portal
#
# Purpose: Script to publish a map service to ArcGIS Portal.
#
# Author: Timo Wicki
#
# Created: 09.03.2023
# -----------------------------------------------------------------------------
import os, sys, logging, json, time, datetime
import arcpy
from arcgis.gis import GIS
from getpass import getpass
import xml.dom.minidom as DOM
from IPython.display import display


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
    paramFiles = sys.argv[1:]
    #paramFiles = [r'C:\Temp\tutorial\publish_citymaps_cache_test.json']
    
    # path to the overall log file if there is more than one json input file (stored in the "Logs" folder in the directory of the Python script).
    overall_log_folder = os.path.join(os.path.dirname(__file__), "Logs")

    count = 0
    portal_url_old =  None
    log_files = []
    total_warnings = 0
    total_errors = 0
    for paramFile in paramFiles:
        if paramFile:        
            with open(paramFile, encoding='utf-8') as f:
                data = json.load(f)
                if 'environment' in data:
                    # if depreciated parameter "environmentan" is used (old json)
                    stage = data["environment"]
                elif "stage" in data:
                    stage = data["stage"]
                else:
                    stage = ""
                portal_url = data["portal_url"]
                federated_server_url = data["federated_server_url"]
                if "sign_in_user" in data:
                    sign_in_user = data["sign_in_user"] 
                else:
                    sign_in_user =  None #default
                if "cert_file" in data:
                    cert_file = data["cert_file"] 
                else:
                    cert_file =  None #default
                if "key_file" in data:
                    key_file = data["key_file"] 
                else:
                    key_file =  None #default
                aprx_name = data["aprx"]
                map_name = data["map"]
                if "layer" in data:
                    layer_name = data["layer"]
                else:
                    layer_name = None #default
                if "table" in data:
                    table_name = data["table"]
                else:
                    table_name = None #default
                service_name = data["service_name"]
                server_folder = data["server_folder"]
                portal_folder = data["portal_folder"]
                service_documents = data["service_documents"]
                if "log_folder" in data:
                    log_folder = data["log_folder"]
                else:
                    log_folder = os.path.join(service_documents, "Logs") #default
                if "service_type" in data:
                    service_type = data["service_type"]
                else:
                    service_type = "MAP_IMAGE" #default
                enable_feature_access = False #default
                if "enable_feature_access" in data:
                    if data["enable_feature_access"] == "True":
                        enable_feature_access = True
                check_unique_ID_assignment = True #default
                if "check_unique_ID_assignment" in data:
                    if data["check_unique_ID_assignment"] == "False":
                        check_unique_ID_assignment = False
                copy_data_to_server = False #default
                if "copy_data_to_server" in data:
                    if data["copy_data_to_server"] == "True":
                        copy_data_to_server = True
                overwrite_existing_service = True #default
                if "overwrite_existing_service" in data:
                    if data["overwrite_existing_service"] == "False":
                        overwrite_existing_service = False
                if "in_startupType" in data:
                    in_startupType = data["in_startupType"]
                else:
                    in_startupType =  "STARTED" #default
                if "share" in data:
                    share = data["share"]
                    share.setdefault("in_override", "OVERRIDE_DEFINITION") #default
                    share.setdefault("in_my_contents", "NO_SHARE_ONLINE") #default
                    share.setdefault("in_public", "PRIVATE") #default
                    share.setdefault("in_organization", "NO_SHARE_ORGANIZATION") #default
                    share.setdefault("in_groups", None) #default
                    # if an "old" JSON file is used, where boolean values are used, instead of the possible values of the corresponding arcgis function parameters
                    if share["in_override"] == "True":
                        share["in_override"] = "OVERRIDE_DEFINITION"
                    elif share["in_override"] == "False": 
                        share["in_override"] = "USE_DEFINITION"  
                    if share["in_my_contents"] == "True":
                        share["in_my_contents"] = "SHARE_ONLINE"
                    elif share["in_my_contents"] == "False":
                        share["in_my_contents"] = "NO_SHARE_ONLINE"    
                    if share["in_public"] == "True":
                        share["in_public"] = "PUBLIC"
                    elif share["in_public"] == "False":
                        share["in_public"] = "PRIVATE"                               
                    if share["in_organization"] == "True":
                        share["in_organization"] = "SHARE_ORGANIZATION"
                    elif share["in_organization"] == "False":
                        share["in_organization"] = "NO_SHARE_ORGANIZATION"                 
                else:
                    share = None
                if "metadata" in data:
                    metadata = data["metadata"]
                    metadata.setdefault("credits", "") #default
                    metadata.setdefault("description", "") #default
                    metadata.setdefault("summary", "") #default
                    metadata.setdefault("tags", "") #default
                    metadata.setdefault("use_limitations", "") #default
                if "enable_cache" in data:
                    enable_cache = data["enable_cache"]
                    enable_cache.setdefault("service_cache_directory", "D:/arcgisserver/directories/arcgiscache") #default
                    enable_cache.setdefault("tiling_scheme_type", "NEW") #default
                    enable_cache.setdefault("scales_type",  "STANDARD") #default
                    enable_cache.setdefault("dots_per_inch",  "96") #default
                    enable_cache.setdefault("tile_size",  "256 x 256") #default    
                    enable_cache.setdefault("cache_tile_format", "PNG") #default    
                    enable_cache.setdefault("storage_format", "COMPACT") #default          
                else:
                    enable_cache = None
                if "manage_cache" in data:
                    manage_cache = data["manage_cache"]
                    manage_cache.setdefault("update_mode", "RECREATE_ALL_TILES") #default
                else:
                    manage_cache = None      
        else:
            print('no Parameter-JSON file specified')
            sys.exit()
        
        ## start logging
        # create logfolder
        create_folder(log_folder)
        if stage == "":
            filename = f'{service_name}'
        else:
            filename = f'{service_name}_{stage.lower()}'

        # path to the log file
        log_file = os.path.join(log_folder, f'{filename}.log')
        # logfile should be unique
        while log_file in log_files:
            log_file = log_file.replace('.log', f'_{count}.log')
        # initialise logging
        init_logging(log_file)
        log_files.append(log_file)
        logger.info(f'******************* Publish service "{service_name}" *******************')
        logger.info(f'Start logging: {time.ctime()}')
        start_time = time.time()

        ## sign in to the portal (only the first time or if portal_url changes)
        if count == 0 or portal_url != portal_url_old:
            logged_in = False
            logger.info(f'Sign in to Portal "{portal_url}"')
        while logged_in == False:
            if sign_in_user:
                pw = getpass(f'Enter password for user "{sign_in_user}": ')
                try:
                    signin = arcpy.SignInToPortal(portal_url, sign_in_user, pw)
                    portal_url_old = portal_url
                    count += 1
                    logged_in = True
                    logger.info(f'Successfully logged in')
                except:
                    logger.info(f'Invalid password for user "{sign_in_user}". Please try again.')
            elif cert_file and key_file:
                    signin = arcpy.SignInToPortal(portal_url, cert_file = cert_file, key_file = key_file)
                    portal_url_old = portal_url
                    count += 1
                    logged_in = True
                    logger.info(f'Successfully logged in')            
            elif cert_file:
                    signin = arcpy.SignInToPortal(portal_url, cert_file = cert_file, password="cert.password")
                    portal_url_old = portal_url
                    count += 1
                    logged_in = True
                    logger.info(f'Successfully logged in')  
                
        ## create sd draft file
        # name of the output files
        try:
            sddraft_filename = os.path.join(service_documents, f'{filename}.sddraft')
            sd_filename = os.path.join(service_documents, f'{filename}.sd')
            # load ArcGIS Pro project
            logger.info("Load arcgis pro project")
            aprx = arcpy.mp.ArcGISProject(aprx_name)
            # list all maps
            map_list = aprx.listMaps(map_name)
            # get the correct map
            found_map = False
            for map in map_list:
                if map.name == map_name:
                    m = map
                    found_map = True
            if not found_map:
                logger.error(f'The map "{map_name}" was not found in the aprx!')
                raise ValueError(f'The map "{map_name}" was not found in the aprx!')
            # define server type
            if stage == "ONLINE":
                server_type = "MY_HOSTED_SERVICES"
            else:
                server_type = "FEDERATED_SERVER"
            # If a layer is specified, only the layer is published, not the entire map.
            if layer_name:
                # list all layers
                layers_list = m.listLayers(layer_name)
                found_layer = False
                # get the correct layer
                for layer in layers_list:
                    if layer.name == layer_name:
                        logger.info(f'The layer "{layer.name}" will be published as service "{service_name}"')
                        # create MapImageSharingDraft
                        sddraft = m.getWebLayerSharingDraft(server_type, service_type, service_name, [layer])
                        logger.info('Created sd draft object')
                        found_layer = True
                if not found_layer:
                    logger.error(f'The layer "{layer_name}" was not found in the aprx!')
                    raise ValueError(f'The layer "{layer_name}" was not found in the aprx!')
            elif table_name:
                # list all tables
                table_list = m.listTables(table_name)
                found_table = False
                # get the correct table
                for table in table_list:
                    if table.name == table_name:
                        logger.info(f'The table "{table.name}" will be published as service "{service_name}"')
                        # create MapImageSharingDraft
                        sddraft = m.getWebLayerSharingDraft(server_type, service_type, service_name, [table])
                        logger.info('Created sd draft object')
                        found_table = True
                if not found_table:
                    logger.error(f'The table "{table_name}" was not found in the aprx!')
                    raise ValueError(f'The table "{table_name}" was not found in the aprx!')
            else: 
                logger.info(f'The map "{m.name}" will be published as service "{service_name}"')
                # create MapImageSharingDraft
                sddraft = m.getWebLayerSharingDraft(server_type, service_type, service_name)       
        except Exception:
            e = sys.exc_info()[1]
            logger.error(f'Creating MapImageSharingDraft failed: {e.args[0]}')
            raise ValueError(f'Creating MapImageSharingDraft failed: {e.args[0]}')
        finally:
            # release ArcGISPro project
            if aprx:
                del aprx       

        logger.info('Update service definition properties')
        # update service definition with basic settings
        sddraft.checkUniqueIDAssignment = check_unique_ID_assignment
        sddraft.copyDataToServer = copy_data_to_server
        sddraft.federatedServerUrl = federated_server_url
        sddraft.overwriteExistingService = overwrite_existing_service
        sddraft.portalFolder = portal_folder
        sddraft.serverFolder = server_folder
        # update service definition with metadata
        if metadata:
            sddraft.credits = metadata["credits"]
            sddraft.description = metadata["description"]
            sddraft.summary = metadata["summary"]
            sddraft.tags = metadata["tags"]
            sddraft.useLimitations = metadata["use_limitations"]
        try:
            # create service Definition draft file
            sddraft.exportToSDDraft(sddraft_filename)
            logger.info(f'Created sd draft file: {sddraft_filename}')
        except Exception:
            e = sys.exc_info()[1]
            logger.error(f'Creating sd draft file failed: {e.args[0]}')
            raise ValueError(f'Creating sd draft file failed: {e.args[0]}')

        ## allow feature access (feature Layer)
        logger.info("Update sddraft file to allow feature access")
        if enable_feature_access:
            # read sd draft file
            doc = DOM.parse(sddraft_filename)
            # find all elements with the name 'TypeName'
            typeNames = doc.getElementsByTagName('TypeName')
            for typeName in typeNames:
                # update TypeName settings
                if typeName.firstChild.data == "FeatureServer":
                    extension = typeName.parentNode
                    for extElement in extension.childNodes:
                        # allow feature access
                        if extElement.tagName == 'Enabled':
                            extElement.firstChild.data = 'true'
            # write result into a new file
            logger.info("Create new sddraft file")
            sddraft_mod_xml_file = os.path.join(service_documents, f'{filename}_mod_xml.sddraft')
            f = open(sddraft_mod_xml_file, 'w')
            # encoding angeben wegen Umlauten
            doc.writexml(f, encoding = "ISO-8859-1")
            f.close()
            # delete the old file
            logger.info("Delete the old sddraft file")
            os.remove(sddraft_filename)
            logger.info("Rename the new sddraft file to have the original name")
            # rename the new file
            os.rename(sddraft_mod_xml_file, sddraft_filename)
            logger.info("Setting 'feature access' activated")
            logger.info("Updated SdDraft file")

        else:
            logger.info("Setting 'feature access' is not activated")

        ## create sd file
        # delete sd file if already exists
        if os.path.exists(sd_filename):
            logger.info("Delete existing sd file")
            os.remove(sd_filename)

        logger.info("Create sd file: Start staging")
        arcpy.server.StageService(sddraft_filename, sd_filename)
        logger.info("Created sd file")
        # alternative : Include automatic registering of database at server
        # stage the service and analyze the .sddraft file for registered data store 
        # continue publishing only if data store is registered
        # stage_service = True
        # analyze and if register data store if not already registered -> add databas as parameter in Input-JSON
        # while stage_service:
        #     arcpy.server.StageService(sddraft_filename, sd_filename)
        #     # Get analyzer warnings to check if data store is registered
        #     warnings = arcpy.GetMessages(1)
        #     logger.warning(warnings)
        #     # If data store is not registered 
        #     if "24011" in warnings:
        #         logger.warning("Datastore is not registered!")
        #         sys.exit()
        #         # Register data store
        #         db_conn = r"C:\Project\db_conn.sde"
        #         register_msg = arcpy.AddDataStoreItem(federated_server_url, "DATABASE", "datastore_name", db_conn)
        #         logger.info(f"registered datastore: {0}".format(register_msg))
        #         # Stage the service again
        #         stage_service = True
        #     else:
        #         stage_service = False
                
        ## publish sd file
        if share:
            logger.info("Publish and share service")
            service = arcpy.server.UploadServiceDefinition(
                    in_sd_file = sd_filename, in_server = federated_server_url, in_startupType = in_startupType, **share
                    )
        else:
            logger.info("Pulish service")
            service = arcpy.server.UploadServiceDefinition(in_sd_file = sd_filename, in_server = federated_server_url, in_startupType = in_startupType)    

        logger.info("published service")
        #display(service)

        ## move service to correct portal folder (bug in publish function above?)
        # When publishing an SD file, an error message appears if the portal folder does not yet exist. 
        # And if it does exist, the item is only displayed under all contents. Therefore the ArcGIS API for Python is used here.
        logger.info('Connect to portal for using ArcGIS API for Python')
        # sign in to the portal (only the first time or if portal_url changes)
        logger.info("Log in at the portal for using the arcgis api for python")
        target = GIS(url=portal_url, username=sign_in_user, password=pw, verify_cert=False)
        logger.info(f"target: {target}")
        # search folders of the singed in user
        create_folder = True
        for folder in target.users.me.folders:
            if portal_folder == folder['title']:
                logger.info(f'Portal folder "{portal_folder}" already exists')
                portal_folder_item = folder
                create_folder = False         
        if create_folder:
            logger.info(f'Create portal folder "{portal_folder}"')
            portal_folder_item = target.content.create_folder(portal_folder) 
        #display(portal_folder_item)  
        # get poral Item of the published service
        target_items_search = target.content.search(query=f"title: {service_name} & owner: {target.users.me.username}")
        if target_items_search:
            # check if exact match
            for item in target_items_search:
                if item.title == service_name:
                    logger.info(f'Move item "{item.title}" of type "{item.type}" to the folder "{portal_folder}"' )
                    item.move(portal_folder, target.users.me.username)
                    #display(item)
                    target_item = item
                else:
                    logger.info(f'Item "{item.title}" does not exactly match..')
        else:
            logger.error(f'Item "{service_name}" could not be found in the portal!')


        ## enable cache
        if enable_cache:
            if "predefined_tiling_scheme" in enable_cache:
                logger.info(f'Create cache scheme with predefined tilling scheme')
            else:
                logger.info(f'Create cache scheme with predefined parameters')
            # define correct url's
            server_rest_url = f'{federated_server_url}' + r'/rest'
            rest_service = service[0].split("arcgis")
            service_url = server_rest_url + rest_service[1]
            try:
                starttime = time.time()
                # create cache
                result = arcpy.server.CreateMapServerCache(service_url, **enable_cache)
                finishtime = time.time()
                elapsedtime = round(finishtime - starttime)
                # log messages to a file
                while result.status < 4:
                    time.sleep(0.2)
                resultValue = result.getMessages()
                logger.info(f'{str(resultValue)} \n')
                logger.info(f'Created cache schmeme for {service_url} in {str(elapsedtime)} sec \n' )         
            except Exception:
                # If an error occurred, log line number and error message
                e = sys.exc_info()[1]
                tb = sys.exc_info()[2]
                logger.error(f'Failed at step 1 \n Line {tb.tb_lineno} \n {str(e)}')
            logger.info(f'Cache enabled for service "{service_name}"')
        else:
            logger.info('Do not create cache')

        # ## restart service (not necessary)     
        # if enable_cache and manage_cache:
        #     # get the ArcGIS feature service that you want to restart
        #     gis_servers = target.admin.servers.list()
        #     # restart specific service
        #     for server in gis_servers:
        #         for service in server.services.list(server_folder):
        #             if service.properties.serviceName == service_name:
        #                 restart = service.restart()
        #                 logger.info(f'Restart service: {restart}')

        ## manage cache
        if manage_cache:
            logger.info('Manage cache')
            if "scales" in manage_cache:
                pass
            elif "update_scales" in manage_cache:
                # if depreciated parameter update_scales is used (old json)
                manage_cache['scales'] = manage_cache.pop['update_scales']
            else:
                # assume that the same scales should be used as in the section enable_cache
                if "scales" in enable_cache:
                    manage_cache['scales'] = enable_cache['scales']
                else:
                    manage_cache['scales'] = ""            
            start_time = time.time()
            scales = manage_cache.pop("scales").split(";")
            for scale in scales:
                # create cache tiles 
                logger.info(f'Create cache tiles for scale "{scale}" - start time: {time.ctime()}')
                try:
                    manage_cache["scales"] = float(scale)
                    starttime = time.time()
                    result = arcpy.server.ManageMapServerCacheTiles(service_url, **manage_cache)
                    while result.status < 4:
                        time.sleep(0.2)
                    finishtime = time.time()
                    elapsedtime = round(finishtime - starttime)
                    resultValue = result.getMessages()
                    logger.info(f'{str(resultValue)} \n')
                    logger.info(f'Cache tiles created for scale "{scale}" in {str(elapsedtime)} sec.\n')
                except Exception:
                    # If an error occurred, print line number and error message
                    e = sys.exc_info()[1]
                    tb = sys.exc_info()[2]
                    logger.error(f'Failed at step 1 \n Line {tb.tb_lineno} \n {str(e)}') 
            logger.info(f'Creation of cache tiles finished for service "{service_name}"')
        else:
            logger.info("Do not create cache tiles")               

        ## end logging
        end_time = time.time()
        i_warning = search(log_file, "warning")
        total_warnings += total_warnings
        i_error = search(log_file, "error")
        total_errors += i_error
        logger.info("Run Script in " + str(round(end_time - start_time)) + " sec.")
        logger.info(f'# {i_error} errors found')
        logger.info(f'# {i_warning} warnings found')
        logger.info(f'End time: {time.ctime()}')
        logger.info('****************************************************************\n')
        logger.handlers.clear()

    # write overall log file
    if count > 1:
        # create overall logfolder
        create_folder(overall_log_folder)
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        with open(os.path.join(overall_log_folder, f'publish_services_{timestamp_str}.log'), 'w') as output_file:
            for log_file in log_files:
                with open(log_file, "r") as input_file:
                    output_file.write(input_file.read())          
            output_file.write('\n****************** Total warnings and errors ******************')
            output_file.write(f'\n# {total_errors} errors found')
            output_file.write(f'\n# {total_warnings} warnings found')
            output_file.write('\n****************************************************************\n')  
