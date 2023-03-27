# JSON file input parameters for publishing webtools to ArcGIS Portal
- A description of the paramters for the script [publish_webtool_portal.py](publish_webtool_portal.py).
- Example JSON files are found in the [tutorial](tutorial) folder.
- A general description of the script is found in the [README.md](../README.md) file.

| Parameter Name|    Description    | Example |
| --- | --- | --- |
| stage | Used for naming the SD files (postfix) that will be created. | "TEST" or "PROD" | 
| portal_url | Path to the ArcGIS Portal on which the web tool is to be published.| "https://xxx.xxx.com/portal"|
| federated_server_url | Path to the ArcGIS Portal Server on which the webtool is to be published.| "https://xxx.xxx.com/server" |
| sign_in_user | User with whom the portal is to be logged in → becomes owner of the published content. Alternatively, use the parameters "cert_file" and "key_file" to log in.| "username@domain" |
| toolbox_name | Path to the toolbox in which the tool is located. | "C:/Temp/tutorial/Schulraumplanung.tbx" |
| tool_name | The name of the tool. | "ExportStandorteVS" |
| tool_parameters | List with all parameters in the correct order (as defined in the tool properties) for running the tool (the tool will be executed before publishing). | ["https://xxx.xxx.xx/rest/services/SLU/Primarschule/FeatureServer/3", "C:/Temp/ExportStandorteVS.xlsx", "True", "True"] |
| service_name | Name of the service that will be created.| "ExportStandorteVS" |
| copy_data_to_server | If "True" the data will be published into the ArcGIS Portal Datastore. If "False" (defaut) the service will reference to the registered database.| "False" |
| overwrite_existing_service | If "True" (default), an existing webtool is overwritten. If "False", an existing service will not be overwritten. | "True" |
| server_folder | Folder on the server in which the webtool is published| "TEST" |
| portal_folder | Folder on the portal interface (in "my content") in which the service is published| "TEST" |
| service_documents | Path in which the SD files will be stored.| "C:/Temp/tutorial" |
| log_folder | Path to the folder where the log file should be saved (default = "path service_documents"/Logs).| "C:/Temp/Logs" |
| server_type | "MY_HOSTED_SERVICES", "ARCGIS_SERVER" (default)  or "FEDERATED_SERVER".| "MY_HOSTED_SERVICES" |
| execution_type | "Synchronous" or "Asynchronous" (default) (see arcpy.CreateGPSDDraft).| "Synchronous" |
| result_map_server | "True" or "False" (default) (see arcpy.CreateGPSDDraft).| "False" |
| show_messages |  The message level e.g. "Info" (default) (see arcpy.CreateGPSDDraft).| "Debug" |
| maximum_records  | e.g. "1000" (default) (siehe arcpy.CreateGPSDDraft).|  "1000" |
| min_instances  | e.g. "1" (default) (siehe arcpy.CreateGPSDDraft).|  "1" |
| max_instances  | e.g. "2" (default) (siehe arcpy.CreateGPSDDraft).|  "2" |
| max_usage_time  | e.g. "600" (default) (siehe arcpy.CreateGPSDDraft).|  "600|
| max_wait_time  | e.g. "60 (default) (siehe arcpy.CreateGPSDDraft).|  "60 |
| max_idle_time  | e.g. "1800" (default) (siehe arcpy.CreateGPSDDraft).|  "1800" |
| capabilities  | "UPLOADS" if a file (e.g. csv file to import) has to be uploaded as an input parameter (see arcpy.CreateGPSDDraft) (optional).|  UPLOADS" |
| constant_values  | Predefined constant values for input parameters (see arcpy.CreateGPSDDraft) (optional).|  "" |
| choice_lists  | Choice lists for input parameters (not yet implemented!) (optional).|  "" |
| share | A dictionary with release settings (optional) → see ArcGIS documentation "arcpy.server.UploadServiceDefinition".| "{...}" |
| share/in_override| "OVERRIDE_DEFINITION" (default) or "USE_DEFINITION". | "OVERRIDE_DEFINITION" |
| share/in_my_contents| "SHARE_ONLINE" (default) or "NO_SHARE_ONLINE".| "SHARE_ONLINE" |
| share/in_public| "PUBLIC" or "PRIVATE" (default).| "PRIVATE" |
| share/in_organization| "SHARE_ORGANIZATION" or "NO_SHARE_ORGANIZATION" (default).| "NO_SHARE_ORGANIZATION" |
| share/in_groups| List of names of groups with which the service is to be shared (optional). | ["testgroup_1", "testgroup_2"] |
| metadata | A dictionary with metadata settings (optional) → see ArcGIS documentation "sddraft parameters".| "{...}" |
| metadata/credits | A string with credit informations. | "© Geoinformationszentrum Stadt Luzern"  |
| metadata/description | A description of the service. | "playground places"  |
| metadata/summary | A summary of the service. | "playground places"  |
| metadata/tags | A string of tags separated by commas.| "test,playground" |
| metadata/use_limitations | A string wit infrmations about use limitation.| "test,playground" |
