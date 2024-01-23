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
from getpass import getpass
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


def get_target_item(target, source_item, replace_urls = None):
    """Get the corresponding target item of the source item

    Required:
        target  -- GIS object (target ArcGIS Portal)
        source_item  -- ArcGIS Portal (source) item object
        replace_urls -- Dictionary with difference between source and target url
    
    Return:
        found_item -- Found ArcGIS Portal (target) item object or None (if not found)
    """ 
    # search for item in target portal 
    target_items_search = target.content.search(query=f'title: "{source_item.title}"', item_type=source_item.type)
    found_item = None
    # check if exact match
    for target_item in target_items_search:
        if not found_item:
            # check if exactly the same title
            if target_item.title == source_item.title:
                try:
                    # item's are only the same if url's are also the same
                    if replace_urls:
                        # check entire url
                        expected_target_url = source_item.url
                        for replace_url in replace_urls:
                            expected_target_url = expected_target_url.replace(replace_url, replace_urls[replace_url])                    
                        if  (target_item.url == expected_target_url) or (target_item.url is None and expected_target_url == '') or (target_item.url == '' and expected_target_url is None):
                            found_item = target_item
                        else:
                            print(f"Found Item '{target_item.title}' does not have the same url (source: {source_item.url}, target:{target_item.url})")    
                    else: 
                        # check only url part after '/rest/'
                        if  target_item.url.split(r"/rest/")[1] == source_item.url.split(r"/rest/")[1]:
                            found_item = target_item
                        else:
                            print(f"Found Item '{target_item.title}' does not have the same url (source: {source_item.url}, target:{target_item.url})")    

                except:
                    # if item's don't have the same rest url assume they are the same
                    found_item = target_item
            else:
                print(f"Found Item '{target_item.title}' does not exactly match..") 

    return found_item


def copy_user(target, source_user, password = None, logger = None):
    """Create user in the target Portal

    Required:
        target  -- GIS object (target ArcGIS Portal)
        source_group -- Group object

    Return:
        copied_user -- Created enterprise User in the target ArcGIS Portal
    """ 
    # create temporary directory for thumbnail 
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # download thumbnail from source Protal
            thumbnail_file = None
            if 'thumbnail' in source_user:
                thumbnail_file = source_user.download_thumbnail(temp_dir)
            # create user
            if source_user.provider == 'arcgis':
                password = getpass(f'Enter password for arcgis build in user "{source_user.fullName}": ')
            copied_user = target.users.create(username=source_user.username, password=password, 
                            firstname=source_user.firstName, lastname=source_user.lastName, 
                            email=source_user.email, provider=source_user.provider, idp_username=source_user.idpUsername, 
                            description=source_user.description, level=int(source_user.level))
            
            # update user role
            if copied_user.roleId != source_user.roleId:
                copied_user.update_role(source_user.roleId)

            # update user infos if necessary
            if copied_user.access != source_user.access:
                copied_user.update(access=source_user.access)
            if copied_user.preferredView != source_user.preferredView:
                copied_user.update(preferred_view=source_user.preferredView)
            if copied_user.tags != source_user.tags:
                copied_user.update(tags=source_user.tags)
            if copied_user.fullName != source_user.fullName:
                copied_user.update(fullname=source_user.fullName)
            if copied_user.culture != source_user.culture:
                copied_user.update(culture=source_user.culture, culture_format=source_user.cultureFormat)
            if copied_user.region != source_user.region:
                copied_user.update(region=source_user.region)       
            if thumbnail_file:
                copied_user.update(thumbnail=thumbnail_file)

            # add user to groups
            for source_group in source_user.groups:
                target_group_search = target.groups.search(source_group.title)
                if target_group_search:
                    # check if match exactly
                    for target_group in target_group_search:    
                        if target_group.title == source_group.title:
                            if logger:
                                logger.info(f"Add user to group '{target_group.title}'")
                            else:
                                print(f"Add user to group '{target_group.title}'")
                            target_group.add_users([copied_user.username])
                        else:
                            print(f"Group '{target_group.title}' does not exactly match..")
                else:
                    if logger:
                        logger.warning(f"Group '{source_group.title}' was not found in the target portal!")
                    else:
                        print(f"Group '{source_group.title}' was not found in the target portal!")

            return copied_user

        except Exception as e:
            print(f"User {source_user.username} kann nicht korrekt erstellt werden:")  
            print(f"{type(e)}: {str(e)}") 
            raise e


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
            

def get_item_mapping(source, target, source_items, source_target_itemId_map = {}, replace_urls = None):
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
        # dependent items
        fd_items = source_item.dependent_upon()
        if fd_items['total'] > 0:
            for fd_item in fd_items['list']:
                if fd_item['dependencyType'] == 'id':
                    source_fd_item = source.content.get(fd_item['id'])
                    # target item abfrufen
                    if source_fd_item.id in source_target_itemId_map.keys():
                        item_mapping[source_fd_item.id] = source_target_itemId_map[source_fd_item.id]
                    else:
                        # get target item
                        found_target_item = get_target_item(target, source_fd_item, replace_urls)

                        if found_target_item:
                            print(f"Found Item '{found_target_item.title}' in target Portal")
                            # item mapping erweitern
                            item_mapping[source_fd_item.id] = found_target_item.id
                        else:
                            print(f"Item '{source_fd_item.title} could not be found in the target Portal!")
                            raise ValueError(f"Item '{source_fd_item.title} could not be found in the target Portal!")

    return item_mapping

print(f'Funktion initialisiert')





