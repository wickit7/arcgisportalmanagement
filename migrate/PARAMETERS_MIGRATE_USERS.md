# JSON file input parameters for migrating ArcGIS Portal Users
- A description of the paramters for the script [0_clone_users.py](0_clone_users.py).
- Example JSON files are found in the [tutorial](tutorial) folder.
- A general description of the script is found in the [README.md](../README.md) file.


| Parameter Name|    Description    | Example |
| --- | --- | --- |
| source_url | Path to the ArcGIS Portal from which the ArcGIS Portal Users will be copied. | "https://xxx.test.com/portal"|
| target_url | Path to the ArcGIS Portal to which the ArcGIS Portal Users will be copied. | "https://xxx.prod.com/portal"|
| sign_in_user | User with whom the portal is to be logged in. Assumption: Same user for "source portal" and "target portal".| "username@domain" |
| clone_user_names | A list of ArcGIS Portal Users to be copied. | ["TestGroup1", "TestGroup2"] |
