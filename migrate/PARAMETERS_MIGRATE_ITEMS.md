# JSON file input parameters for migrating ArcGIS Portal Items
- A description of the paramters for the script [3_clone_items.py](3_clone_items.py).
- Example JSON files are found in the [tutorial](tutorial) folder.
- A general description of the script is found in the [README.md](../README.md) file.

The same sharing options as the item in the "source" Portal will be used for the item in the "target" Portal. 

| Parameter Name|    Description    | Example |
| --- | --- | --- |
| source_url | Path to the ArcGIS Portal from which the ArcGIS Portal Items will be copied. | "https://xxx.test.com/portal"|
| target_url | Path to the ArcGIS Portal to which the ArcGIS Portal ITems will be copied. | "https://xxx.prod.com/portal"|
| sign_in_user | User with whom the portal is to be logged in. Assumption: Same user for "source portal" and "target portal".| "username@domain" |
| replace_urls |A dictionary with the URLs to be replaced in app configuration ( "search & replace" in the item's JSON) e.g. A geocode service can may be updated like this or a PDF hyperlink (optional). | {"/test.": "/prod."} |
| clone_source_items | A dictionary with the portal items to be cloned. → see gis.content.clone_items(). | {...} |
| clone_source_items/item_id | ItemID of the item in the source portal (e.g. PDF, Web Map, Web Mapping Application). | "b573ca4e4a2a4b3db4eae797f36678ae" |
| clone_source_items/folder | Portal folder in which the items are to be stored. | "Test" |
| clone_source_items/preserve_item_id | "True" if the item in the target Portal should have the same Id as in the source Portal (recommended). If "False" (default), a new Id is generated for the Item in the target Portal. | "Test" |
| clone_source_items/item_extent | Spatial extent for the items to be cloned (optional). | - |
| clone_source_items/use_org_basemap | "True" (default) if the standard basemap of the target portal is to be used. "False" if the standard basemap of the target portal is not to be used. | - |
| clone_source_items/copy_data | If "False", the data is stored as a reference and not as a copy. The default is "True", the data is copied. This creates a hosted feature collection or feature layer. We publish the feature layers with the publishing script ([publih](publish)) and only clone items that do not directly reference database such as web maps and web map applications. Automatically set to "True" if Item is hosted. (optional) | - |
| clone_source_items/copy_global_ids | Requires that the previous parameter is set to True. If True, the copied features retain their global IDs. Default is False (optional). Automatically set to True if Item is hosted. (optional). | - |
| clone_source_items/search_existing_items | Specifies whether elements that have already been cloned should be searched for in the target Portal and reused instead of being cloned again. "True" (default) or "False". | - |

Notes:
- In the JSON, check the order when listing the items to be cloned!First, list the items that are not dependent on the items listed after them. If, for example, a web map application is cloned, all included items (e.g. maps, layers) should already be cloned.
- BUG-000150518: Python API's clone_items Fails to clone web application Items between two ArcGIS Portals when preserve_item_id parameter is "True".
