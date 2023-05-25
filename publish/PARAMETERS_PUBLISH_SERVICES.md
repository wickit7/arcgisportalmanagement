# JSON file input parameters for publishing services to ArcGIS Portal
- A description of the paramters for the script [publish_service_portal.py](publish_service_portal.py).
- Example JSON files are found in the [tutorial](tutorial) folder.
- A general description of the script is found in the [README.md](../README.md) file.


| Parameter Name|    Description    | Example |
| --- | --- | --- |
| stage | Used for naming the SD files (postfix) that will be created. It also specifies the server type (if "ONLINE" → server_type = "MY_HOSTED_SERVICES".  Otherwise server_type = "FEDERATED_SERVER").| "TEST" or "PROD" | 
| portal_url | Path to the ArcGIS Portal on which the service is to be published.| "https://xxx.xxx.com/portal"|
| federated_server_url | Path to the ArcGIS Portal Server on which the service is to be published.| "https://xxx.xxx.com/server" |
| sign_in_user | User with whom the portal is to be logged in → becomes owner of the published content. Alternatively, use the parameters "cert_file" and "key_file" to log in.| "username@domain" |
| aprx | Path to the ArcGIS Pro project with the maps/layers to be published.| "C:/Temp/tutorial/tutorial.aprx" |
| map | Name of the map in the ArcGIS Pro project with the data to be published.| "citymaps_editor" |
| layer | Name of the layer to be published. If no layer (or table) is specified, the entire map is published (optional). | "Playground" |
| table | Name of the table to be published. If no table (or layer) is specified, the entire map is published (optional). | "Items" |
| service_name | Name of the service that will be created.| "Playground" |
| server_folder | Folder on the server in which the service is published| "TEST" |
| portal_folder | Folder on the portal interface (in "my content") in which the service is published| "TEST" |
| service_type | "FEATURE", "TILE" or "MAP_IMAGE" (default).| "MAP_IMAGE" |
| service_documents | Path in which the SD files will be stored.| "C:/Temp/tutorial" |
| log_folder | Path to the folder where the log file should be saved (default = "path service_documents"/Logs).| "C:/Temp/Logs" |
| enable_extensions | A list of extenstions that are enabled after publishing the service. Possible entries are: FeatureServer, WMSServer, WFSServer, NetworkDiagramServer, TopographicProductionServer, TraceNetworkServer, ValidationServer, WCSServer, LRServer, ParcelFabricServer, VersionManagementServer, KmlServer, UtilityNetworkServer. (optional)| ["FeatureServer" ,"WMSServer", "WFSServer"] |
| check_unique_ID_assignment | A Boolean that indicates whether your map is analyzed to confirm that the Allow assignment of unique numeric IDs for sharing web layers option in Map Properties is enabled (optional). | "True" (default)|
| copy_data_to_server | If "True" the data will be published into the ArcGIS Portal Datastore. If "False" (defaut) the service will reference to the registered database.| "False" |
| overwrite_existing_service | If "True" (default), an existing service is overwritten. If "False", an existing service will not be overwritten. | "True" |
| in_startupType | If "STARTED" (default) service will be started after publishing. If "STOPPED" service will not start automatically. → see ArcGIS documentation "arcpy.server.UploadServiceDefinition".| "STARTED" |
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
| enable_cache | If a cache scheme is to be created for the service (optional) → see arcpy.server.CreateMapServerCache()| "{...}" |
| enable_cache/service_cache_directory | Path to "arcgiscache" Directory on the server e.g. "D:/arcgisserver/directories/arcgiscache" (default).|"D:/arcgisserver/directories/arcgiscache" |
| enable_cache/tiling_scheme_type | "NEW" (default) or "PREDEFINED" (if predefined tiling scheme file XML is used).| "NEW"|
| enable_cache/scales_type | "STANDARD" (default) or "CUSTOM".|"STANDARD"|
| enable_cache/num_of_scales | Number of scales.| "10" |
| enable_cache/dots_per_inch | Dots per inch.| "96" (default) |
| enable_cache/tile_size | Tile size. | "256 x 256" (default) |
| enable_cache/predefined_tiling_scheme | Path to tiling scheme XML file (optional). | "C:/Temp/tutorial/tiling schema/Tilingschema_slu.xml" |
| enable_cache/tile_origin | Origin of the tiles. | "-27386400 31814500" (optional) |
| enable_cache/scales | Scales separated by semicolons. (optional)|  "25000;10000;5000;2000;1000;500;200"  |
| enable_cache/cache_tile_format | Cache tile format.| "PNG" (default) |
| enable_cache/tile_compression_quality | Tile compression quality.| "0" (default) |
| enable_cache/storage_format | "COMPACT" (default) or "EXPLODED".| "COMPACT" |
| manage_cache | If cache tiles are to be created (optional) → see arcpy.server.ManageMapServerCacheTiles()| "{...}" |
| manage_cache/scales | Usually the same as for the paramter "scales" in the section "enable_cache" (default) | "25000;10000"|
| manage_cache/update_mode | "RECREATE_EMPTY_TILES", "RECREATE_ALL_TILES" (default) or "DELETE_TILES". | "RECREATE_ALL_TILES"|
| manage_cache/num_of_caching_service_instances | Number of instances used to calculate the cache tiles (optional).| "3"|
| manage_cache/update_extent | Rectancular extend for which the cache should be calculated (optional). | "2663236.84315087 1209883.76599764 2667648.37450472 1212477.32630589"|
| manage_cache/wait_for_job_completion | "WAIT" (default) or "DO_NOT_WAIT".| "WAIT"|


