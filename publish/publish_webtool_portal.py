# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: publish_webtool_portal
#
# Purpose: Script to publish a python webtool to ArcGIS Portal.
#
# Author: Timo Wicki
#
# Created: 20.03.2023
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
    #paramFiles = [r'C:\temp\tutorial\publish_webtool_ExportStandorteVS_test.json']

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
                    cert_file =  None
                if "key_file" in data:
                    key_file = data["key_file"] 
                else:
                    key_file =  None
                toolbox_name = data["toolbox_name"]
                tool_name = data["tool_name"]
                tool_parameters = data["tool_parameters"]
                service_name = data["service_name"]
                server_folder = data["server_folder"]
                portal_folder = data["portal_folder"]
                service_documents = data["service_documents"]            
                copy_data_to_server = False #default
                if "server_type" in data:
                    server_type = data["server_type"]
                else:
                    server_type = "ARCGIS_SERVER" #default
                if "copy_data_to_server" in data:
                    if data["copy_data_to_server"] == "True":
                        copy_data_to_server = True
                overwrite_existing_service = True #default
                if "overwrite_existing_service" in data:
                    if data["overwrite_existing_service"] == "False":
                        overwrite_existing_service = False
                if "execution_type" in data:
                    execution_type = data["execution_type"]
                else:
                    execution_type = "Asynchronous" #default
                result_map_server = False #default
                if "result_map_server" in data:
                    if data["result_map_server"] == "True":
                        result_map_server = True
                if "show_messages" in data:
                    show_messages = data["show_messages"]
                else:
                    show_messages = "Info" #default
                if "maximum_records" in data:
                    maximum_records = int(data["maximum_records"])
                else:
                    maximum_records = 1000 #default
                if "min_instances" in data:
                    min_instances = int(data["min_instances"])
                else:
                    min_instances = 1 #default
                if "max_instances" in data:
                    max_instances = int(data["max_instances"])
                else:
                    max_instances = 2 #default
                if "max_usage_time" in data:
                    max_usage_time = int(data["max_usage_time"])
                else:
                    max_usage_time = 600 #default
                if "max_wait_time" in data:
                    max_wait_time = int(data["max_wait_time"])
                else:
                    max_wait_time = 60 #default
                if "max_idle_time" in data:
                    max_idle_time = int(data["max_idle_time"])
                else:
                    max_idle_time = 1800 #default
                if "capabilities" in data:
                    capabilities = data["capabilities"]
                else:
                    capabilities = None
                if "constant_value" in data:
                    constant_values = data["constantValues"]
                else:
                    constant_values = None
                if "choice_lists" in data:
                    choice_lists = data["choice_lists"]
                else:
                    choice_lists = None
                if "log_folder" in data:
                    log_folder = data["log_folder"]
                else:
                    log_folder = os.path.join(service_documents, "Logs") #default
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
        logger.info(f'******************* Publish webtool "{service_name}" *******************')
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
                
        ## Execute Tool
        try:
            # import toolbox
            toolbox = arcpy.ImportToolbox(toolbox_name)
            # create function object
            tool = getattr(toolbox,  tool_name)
            # execute tool
            logger.info("Execute tool")
            result = tool(*tool_parameters)
            logger.info(result.getMessages())

        except Exception:
            e = sys.exc_info()[1]
            logger.error(f'Executing tool failed: {e.args[0]}')
            raise ValueError(f'Executing tool failed: {e.args[0]}')
            
        finally:
            if tool:
                del tool
            if toolbox:
                del toolbox       
        
        ## create sd draft file
        logger.info("Create SdDraft file")
        try:
            # name of the output files
            sddraft_filename = os.path.join(service_documents, f'{filename}.sddraft')
            sd_filename = os.path.join(service_documents, f'{filename}.sd')
            logger.info(f'The tool "{tool_name}" will be published as webtool "{service_name}"')
            # Create service definition draft and return analyzer messages
            analyzeMessages = arcpy.CreateGPSDDraft(
                result, sddraft_filename, service_name, server_type=server_type,
                copy_data_to_server=copy_data_to_server, folder_name=server_folder, 
                summary=metadata['summary'], tags=metadata['tags'], executionType=execution_type,
                resultMapServer=result_map_server, showMessages=show_messages, maximumRecords=maximum_records,
                minInstances=min_instances, maxInstances=max_instances, maxUsageTime=max_usage_time, maxWaitTime=max_wait_time,
                maxIdleTime=max_idle_time, capabilities=capabilities, constantValues = constant_values) 
            if analyzeMessages['warnings'] != {}:
                logger.warning(analyzeMessages['warnings'])
            if analyzeMessages['errors'] != {}:
                logger.error(analyzeMessages['errors'])
                logger.info("Created SdDraft file")
        except Exception:
            e = sys.exc_info()[1]
            logger.error(f'Creating SdDraft file failed: {e.args[0]}')
            raise ValueError(f'Creating SdDraft file failed: {e.args[0]}')

        ## edit sd draft file
        try:
            logger.info("Edit SdDraft file")
            # allow overwriting the webtool ("https://www.spatialtimes.com/2019/09/python-script-to-overwrite-existing-service-in-arcgis-server/")
            # read the file
            with open(sddraft_filename, 'r') as file:
                filedata = file.read()
            if overwrite_existing_service:
                # Replace the target string 
                filedata = filedata.replace('esriServiceDefinitionType_New', 'esriServiceDefinitionType_Replacement')
                logger.info("Allow overwriting the webtool")
            # Write the file out again
            with open(sddraft_filename, 'w') as file:
                file.write(filedata)
            logger.info("SdDraft-Datei bearbeitet")
        except Exception:
            e = sys.exc_info()[1]
            logger.error(f'Editing SdDraft file failed: {e.args[0]}')
            raise ValueError(f'Editing SdDraft file failed: {e.args[0]}')

        ## create sd file
        try:
            # delete sd file if already exist
            if os.path.exists(sd_filename):
                logger.info("Delete existing sd file")
                os.remove(sd_filename)
            if analyzeMessages['errors'] == {}:
                logger.info("Create SD file: Start staging")
                arcpy.server.StageService(sddraft_filename, sd_filename)
                logger.info("Created SD file")
            else:
                # if the sddraft analysis contained errors, display them
                logger.info(analyzeMessages['errors'])
        except Exception:
            e = sys.exc_info()[1]
            logger.error(f'Creating SD file failed: {e.args[0]}')
            raise ValueError(f'Creating SD file failed: {e.args[0]}')
                
        ## publish sd file
        if share:
            logger.info("Publish and share service")
            service = arcpy.server.UploadServiceDefinition(
                    in_sd_file = sd_filename, in_server = federated_server_url, **share
                    )
        else:
            logger.info("Pulish service")
            service = arcpy.server.UploadServiceDefinition(in_sd_file = sd_filename, in_server = federated_server_url)    
        logger.info("published service")
        #display(service)

        ## update portal item and move it to the correct portal folder (bug in publish function above?)
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
                    # Item Properties aktualisieren
                    credits = metadata["credits"]
                    use_limitations = metadata["use_limitations"]
                    description = metadata["description"]
                    item_properties = {'licenseInfo': use_limitations, 'accessInformation':credits, 'description': description}
                    item.update(item_properties)
                    #display(item)
                    target_item = item
                else:
                    logger.info(f'Item "{item.title}" does not exactly match..')
        else:
            logger.error(f'Item "{service_name}" could not be found in the portal!')

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
        with open(os.path.join(overall_log_folder, f'publish_webtools_{timestamp_str}.log'), 'w') as output_file:
            for log_file in log_files:
                with open(log_file, "r") as input_file:
                    output_file.write(input_file.read())          
            output_file.write('\n****************** Total warnings and errors ******************')
            output_file.write(f'\n# {total_errors} errors found')
            output_file.write(f'\n# {total_warnings} warnings found')
            output_file.write('\n****************************************************************\n')  
