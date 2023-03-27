# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name: portal_management_functions 
# 
# Purpose: Custom functions to manage the ArcGIS Portal with the ArcGIS Python API.
#
# Author: Timo Wicki
#
# Created: 20.03.2023
# -----------------------------------------------------------------------------
import tempfile

from arcgis.gis import GIS

## globale variables
# sign in Portal user
SIGN_IN_USERNAME = "portaladmin" #default
# possible options
TEXT_BASED_ITEM_TYPES = frozenset(['Web Map', 'Feature Service', 'Map Service','Web Scene',
                                  'Image Service', 'Feature Collection', 
                                   'Feature Collection Template', 'Web Mapping Application', 
                                   'Mobile Application', 'Symbol Set', 'Color Set', 
                                   'Windows Viewer Configuration'])
FILE_BASED_ITEM_TYPES = frozenset(['File Geodatabase','CSV', 'Image', 'KML', 'Locator Package',
                                 'Map Document', 'Shapefile', 'Microsoft Word', 'PDF',
                                 'Microsoft Powerpoint', 'Microsoft Excel', 'Layer Package',
                                 'Mobile Map Package', 'Geoprocessing Package', 'Scene Package',
                                 'Tile Package', 'Vector Tile Package'])
RELATIONSHIP_TYPES = frozenset(['Map2Service', 'WMA2Code',
                                'Map2FeatureCollection', 'MobileApp2Code', 'Service2Data',
                                'Service2Service'])
# Item Types where URLs in the entire text ('get_data()') are to be replaced. Maybe need to be extended..
REPLACE_URLS_TYPES = frozenset(['Web Mapping Application', 'Mobile Application'])


def is_hosted(item):
    """Check if it is a hosted item

    Required:
        item  -- ArcGIS Portal item object
    
    Return:
        Boolean
    """ 
    # check if Item contains the keyword "Hosted"
    if [keyword for keyword in item.typeKeywords if "Hosted" in keyword]:
        return True
    else:
        return False


def copy_user(target, source_user):
    """Create user in the target Portal

    Required:
        target  -- GIS object (target ArcGIS Portal)
        source_group -- Group object

    Return:
        copied_user -- Created enterprise User in the target ArcGIS Portal
    """ 
    # create temporary directory for thumbnail 
    with tempfile.TemporaryDirectory() as temp_dir:
        # first- und lastname of the source user
        try:
            first_name = source_user.firstName
            last_name = source_user.lastName
        except:
            full_name = source_user.fullName
            first_name = full_name.split()[0]
            try:
                last_name = full_name.split()[1]
            except:
                last_name = 'None'
        try:    
            # download thumbnail from source Protal
            if 'thumbnail' in source_user:
                thumbnail_file = source_user.download_thumbnail(temp_dir)
            # create user 
            copied_user = target.users.create(username=source_user.username, password='None', 
                            firstname=first_name, lastname=last_name, email=source_user.email, 
                            description=source_user.description, provider="enterprise", 
                            idp_username=source_user.idpUsername, level=int(source_user.level))
            # update user infos
            copied_user.update(access=source_user.access, preferred_view=source_user.preferredView, 
                                tags=source_user.tags, thumbnail = thumbnail_file, fullname=source_user.fullName, 
                                culture=source_user.culture, region=source_user.region)
            # update user role
            copied_user.update_role(source_user.roleId)

            return copied_user

        except Exception as e:
            print(f"User {source_user.username} kann nicht korrekt erstellt werden:")  
            print(f"{type(e)}: {str(e)}") 
            raise 


def copy_group(target, source_group, group_copy_properties=None):
    """Create group in the target ArcGIS Portal

    Required:
        target  -- GIS object (target ArcGIS Portal)
        source_group -- Group object
        group_copy_properties -- Dictionary "parameter:value" as input for target.groups.create_from_dict. 
                                 If the parameter is not defined, all properties are transferred (v. 1.8.3).
    
    Return:
        copied_group -- Created group in the target ArcGIS Portal
    """  
    # settings to be copied
    if not group_copy_properties:
        group_copy_properties = ['title', 'isInvitationOnly', 'owner', 'description', 'snippet', 
                                 'tags', 'phone', 'sortField', 'sortOrder', 'isViewOnly', 'thumbnail',
                                 'access', 'capabilities', 'isReadOnly', 'protected', 'autoJoin', 
                                 'notificationsEnabled', 'provider', 'providerGroupName', 'leavingDisallowed',
                                 'hiddenMembers', 'displaySettings']
    
    # create temporary directory for thumbnail 
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            target_group = {}
            # take over all settings from source group
            for property_name in group_copy_properties:
                #print(f"{property_name}: {source_group[property_name]}")
                if source_group[property_name] == []:
                    target_group[property_name] = None
                else:
                    target_group[property_name] = source_group[property_name]
            # download thumbnail from source Protal
            if 'thumbnail' in source_group:
                target_group['thumbnail'] = source_group.download_thumbnail(temp_dir)
            # create group
            copied_group = target.groups.create_from_dict(target_group)
            # assign the correct owner to the group and add members.
            members = source_group.get_members()
            if not members['owner'] == SIGN_IN_USERNAME:
                copied_group.reassign_to(members['owner'])
            if members['users']:
                copied_group.add_users(members['users'])
            return copied_group
        
        except Exception as e:
            print(f"Error creating {source_group['title']}:")
            print(f"{type(e)}: {str(e)}")
            raise
            

def get_item_mapping(source, target, source_items, source_target_itemId_map = {}):
    """Search for all dependent items and create an item mapping between source and target IDs.

    Required:
        source_items  -- List of source ArcGIS Portal items.
        source_target_itemId_map -- Dictionary "source ID:target ID" mapping the source items with the target items. 
                                    Needed because recently created items are sometimes not found already.

    Return:
        item_mapping --  Dictionary "source ID:target ID" mapping the source items with the target items. 
    """  
    item_mapping = {}
    for source_item in source_items:
        fd_items = source_item.dependent_upon()
        if fd_items['total'] > 0:
            for fd_item in fd_items['list']:
                if fd_item['dependencyType'] == 'id':
                    source_fd_item = source.content.get(fd_item['id'])
                    # target item abfrufen
                    if source_fd_item.id in source_target_itemId_map.keys():
                        item_mapping[source_fd_item.id] = source_target_itemId_map[source_fd_item.id]
                    else:
                        # nach item in target suchen 
                        target_fd_items_search = target.content.search(query=f"title: {source_fd_item.title}", item_type=source_fd_item.type)
                        if target_fd_items_search:
                            # prüfen ob exakte Übereinstimmung
                            for target_fd_item in target_fd_items_search:
                                if target_fd_item.title == source_fd_item.title:
                                    print(f"Found Item '{target_fd_item.title}' in target Portal")
                                    # item mapping erweitern
                                    item_mapping[source_fd_item.id] = target_fd_item.id
                                else:
                                    print(f"Found Item '{target_fd_item.title}' does not exactly match..") 

                        else:
                            print(f"Item '{source_fd_item.title} could not be found in the target Portal!")
                            raise ValueError(f"Item '{source_fd_item.title} could not be found in the target Portal!")

    return item_mapping

print(f'Funktion initialisiert')





