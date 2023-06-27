# ArcGIS Enterprise-Portal: Scripts for publishing services and migrating items (arcgisportalmanagement)
The scripts are designed to automate tasks in the ArcGIS Portal environment. JSON files are used to execute the scripts with the desired parameters.

## Publishing ArcGIS Services
The script [publish_service_portal.py](publish/publish_service_portal.py) can be used to pusblish ArcGIS Services like MapServer, FeatureServer, WFS or WMS. In the folder [tutorial](publish/tutorial) there are several json sample files:

- [publish_playground_test.json](publish/tutorial/publish_playground_test.json): Publish a web feature layer with feature access (FeatureServer) (for publishing a standalone table use the parameter "table" instead of "layer")
- [publish_citymaps_cache_test.json](publish/tutorial/publish_citymaps_cache_test.json): Publish a web feature layer, define cache schema and create cache tiles.
- [publish_citymaps_cache_predefined_test.json](publish/tutorial/publish_citymaps_cache_predefined_test.json): Publish a web feature layer, define a cache schema based on a schema-file (xml) and create cache tiles.
- [publish_playground_ogc_test.json](publish/tutorial/publish_playground_ogc_test.json): Publish a web feature layer with the extensions "FeatureServer" and "WMSServer" (OGC WMS) and "WFSServer" (OGC WFS).


The JSON schema and the set of JSON parameters that can be used are described in the README file [PARAMETERS_PUBLISH_SERVICES.md](publish/PARAMETERS_PUBLISH_SERVICES.md).

## Publishing ArcGIS webtools
The script [publish_webtool_portal.py](publish/publish_webtool_portal.py) can be used to pusblish an ArcGIS webtool. A sample json file is found in the folder [tutorial](publish/tutorial):

- [publish_webtool_ExportStandorteVS_test.json](publish/tutorial/publish_webtool_ExportStandorteVS_test.json): Publish a webtool with which data sets can be exported to an Excel file.

The JSON schema and the set of JSON parameters that can be used are described in the README file [PARAMETERS_PUBLISH_WEBTOOL.md](publish/PARAMETERS_PUBLISH_WEBTOOL.md).

## Migrate ArcGIS Portal Users
The script [0_clone_users.py](migrate/0_clone_users.py) can be used to migrate ArcGIS Portal Users from one Portal (e.g. test stage) to another Portal (e.g. productive stage). A sample json file is found in the folder [tutorial](migrate/tutorial):

- [0_clone_users.json](migrate/tutorial/0_clone_users.json): Migrate ArcGIS Portal Users.

The JSON schema and the set of JSON parameters that can be used are described in the README file [PARAMETERS_MIGRATE_USERS.md](migrate/PARAMETERS_MIGRATE_USERS.md).

## Migrate ArcGIS Portal Groups
The script [1_clone_groups.py](migrate/1_clone_groups.py) can be used to migrate ArcGIS Portal Groups from one Portal (e.g. test stage) to another Portal (e.g. productive stage). A sample json file is found in the folder [tutorial](migrate/tutorial):

- [1_clone_groups.json](migrate/tutorial/1_clone_groups.json): Migrate ArcGIS Portal Groups.

The JSON schema and the set of JSON parameters that can be used are described in the README file [PARAMETERS_MIGRATE_GROUPS.md](migrate/PARAMETERS_MIGRATE_GROUPS.md).

## Migrate ArcGIS Portal Items
After publishing referenced services to different stages ([publish](publish)), the script [3_clone_items.py](migrate/3_clone_items.py) can be used to migrate ArcGIS Portal Items (e. g. hosted services, Web Map's or Web Map Application's) from one Portal (e.g. test stage) to another Portal (e.g. productive stage). A sample json file is found in the folder [tutorial](migrate/tutorial):

- [3_clone_items.json](migrate/tutorial/3_clone_items.json): Migrate ArcGIS Portal Items.

The JSON schema and the set of JSON parameters that can be used are described in the README file [PARAMETERS_MIGRATE_ITEMS.md](migrate/PARAMETERS_MIGRATE_ITEMS.md).

## Contributing
Contributions to this project are welcome! If you have any suggestions or bug reports, please open an issue or pull request on GitHub.

## License
This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE.txt) file for more information.

## Acknowledgements
This project includes the arcpy package from Esri (Copyright © 1995-2022 Esri), which is subject to its own license terms. Please refer to the Esri license agreement for more information.
