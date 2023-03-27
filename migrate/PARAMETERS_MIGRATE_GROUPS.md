# JSON file input parameters for migrating ArcGIS Portal Groups
- A description of the paramters for the script [1_clone_groups.py](1_clone_groups.py).
- Example JSON files are found in the [tutorial](tutorial) folder.
- A general description of the script is found in the [README.md](../README.md) file.

The same ArcGIS Portal Users as in the group of the "source" Portal will be assigned to the group in the "target" Portal.

| Parameter Name|    Description    | Example |
| --- | --- | --- |
| source_url | Path to the ArcGIS Portal from which the ArcGIS Portal Groups will be copied. | "https://xxx.test.com/portal"|
| target_url | Path to the ArcGIS Portal to which the ArcGIS Portal Groups will be copied. | "https://xxx.prod.com/portal"|
| sign_in_user | User with whom the portal is to be logged in. Assumption: Same user for "source portal" and "target portal".| "username@domain" |
| clone_group_names | A list of ArcGIS Portal Groups to be copied. | ["TestGroup1", "TestGroup2"] |
