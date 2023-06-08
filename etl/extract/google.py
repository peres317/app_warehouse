import requests
import base64
from lxml.etree import XML
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from alive_progress import alive_bar
import json
from os import path, remove

from common.domain.android_permission import AndroidPermission
from common.domain.android_permission_group import AndroidPermissionGroup
from common.util import Util as u


class ProtectionLevel:
    """Represent protection level map. Data extracted from Android developers 
    web.
    """
    
    MAP = {
        "0x00030D40": "appPredictor",
        "0x00000028": "appop",
        "0x000C3500": "companion",
        "0x00013880": "configurator",
        "0x00000001": "dangerous",
        "0x00000014": "development",
        "0x000186A0": "incidentReportApprover",
        "0x00000064": "installer",
        "0x000003E8": "instant",
        "0x00000004": "internal",
        "0x007A1200": "knownSigner",
        "0x00061A80": "module",
        "0x00000000": "normal",
        "0x00000FA0": "oem",
        "0x00000050": "pre23",
        "0x00000190": "preinstalled",
        "0x0000000A": "privileged",
        "0x001E8480": "recents",
        "0x000F4240": "retailDemo",
        "0x003D0900": "role",
        "0x000007D0": "runtime",
        "0x00000320": "setup",
        "0x00000002": "signature",
        "0x00000003": "signatureOrSystem",
        "0x00001F40": "vendorPrivileged",
        "0x000000C8": "verifier"
    }
    
    @staticmethod
    def to_str(hex_values: str) -> str:
        """Convert hex protection level values to string representation.

        Args:
            hex_values (str): Protection levels on hex values.

        Returns:
            str: Protection levels on human readable string.
        """
        hex_values = hex_values.split("|")
        p_levels = [ProtectionLevel.MAP[hex_value] for hex_value in hex_values]
        return "|".join(p_levels)
    
    
class AndroidDevelopersWeb:
    """Represents Android developers web.
    """
    
    PERMISSION_URL = ("https://developer.android.com/"
                      "reference/android/Manifest.permission")
    GROUP_URL = ("https://developer.android.com/"
                 "reference/android/Manifest.permission_group")
    SLEEP_TIME = 1
    TIMEOUT = 5
    
    def __init__(self, url: str) -> None:
        """Creates an AndroidDevelopersWeb object.

        Args:
            url (str): Url of page. It can be 
                AndroidDevelopersWeb.PERMISSION_URL or
                AndroidDevelopersWeb.GROUP_URL.
        """
        u.log_normal("Finding content on " + url + "...")
        
        # Load page
        self.driver = webdriver.Firefox()
        self.driver.get(url)
        
        # Wait for content
        end_time = time.time() + self.TIMEOUT
        while(len(self.driver.find_elements(By.TAG_NAME, "h3")) == 0):
            time.sleep(self.SLEEP_TIME)
            if(time.time() > end_time):
                u.log_error("Timeout.", "Could not load page %s." % url)
                break
        
        # Store content
        element_list = self.driver.find_elements(By.TAG_NAME, "h3")
        element_ids = map(lambda x: x.get_attribute("id"), element_list)
        self.element_list = list(zip(element_ids, element_list))
        
        u.log_result("%d elements found." % len(self.element_list))
        
    def get_added_in_api_level(self, element_id: str) -> str:
        """Finds added in api level attribute of element with element_id on 
        webpage.

        Args:
            element_id (str): Id of the element we want.

        Returns:
            str: Added in API level attribute. None if not found.
        """
        id = element_id.split(".")[-1]
        permission = filter(lambda idp:idp[0] == id, self.element_list)
        try:
            idp = next(permission)
            parent = idp[1].find_element(By.XPATH, '..')
            api_level = parent.get_attribute("data-version-added")
            
            return api_level
        except Exception:
            u.log_warning("Empty list.", element_id + " api level not found.")
        return None
    
    def close_driver(self):
        """Close browser.
        """
        self.driver.close()  
        
        
class BaseFrameworkAndroidManifest:
    """Represents AndroidManifest on master branch from 
    android.googlesource.com.
    """
    
    URL = ("https://android.googlesource.com/platform/frameworks/base.git/+/"
           "refs/heads/master/core/res/AndroidManifest.xml?format=TEXT")
    LOCAL_PERMISSION = "data/google_downloads/permission.json"
    LOCAL_GROUPS = "data/google_downloads/groups.json"
         
    def __init__(self) -> None:
        """Creates a BaseFrameworkAndroidManifest object.
        """
        u.log_normal("Downloading Android AndroidManifest.xml...")
        
        # Downloading AndroidManifest
        r = requests.get(self.URL)
        if r.status_code != 200:
            u.log_error("Timeout.", "Could not download Android " 
                        + "AndroidManifest.xml.")
        xml = XML(base64.b64decode(r.text))
        
        # Look for relevant elements
        self.permission_list = xml.findall("permission")
        self.permission_group_list = xml.findall("permission-group")
        self.permission_web = AndroidDevelopersWeb(
            AndroidDevelopersWeb.PERMISSION_URL
        )
        self.permission_group_web = AndroidDevelopersWeb(
            AndroidDevelopersWeb.GROUP_URL
        )
        
        u.log_result("AndroidManifest downloaded.")
        
    def download_all_data(self, local: bool = False):
        """Download permissions and groups from manifest and stores on default
        dirs.

        Args:
            local (bool, optional): If you want local stored results. Defaults 
                to False.
        """
        u.log_normal("Extracting groups and permissions from " 
                     + "AndroidManifest.xml...")
        
        if(local and path.exists(BaseFrameworkAndroidManifest.LOCAL_GROUPS) 
           and path.exists(BaseFrameworkAndroidManifest.LOCAL_PERMISSION)):
            # All data were downloaded previously
            
            self.permission_group_web.close_driver()
            self.permission_web.close_driver()
            return
        
        # Remove old data
        if path.exists(BaseFrameworkAndroidManifest.LOCAL_GROUPS):
            remove(BaseFrameworkAndroidManifest.LOCAL_GROUPS)
        if path.exists(BaseFrameworkAndroidManifest.LOCAL_PERMISSION):
            remove(BaseFrameworkAndroidManifest.LOCAL_PERMISSION)
        
        # Extract new data
        with open(BaseFrameworkAndroidManifest.LOCAL_GROUPS, "+a") as f:
            f.write(json.dumps(self.get_aosp_permission_groups(), indent=2))
        with open(BaseFrameworkAndroidManifest.LOCAL_PERMISSION, "+a") as f:
            f.write(json.dumps(self.get_aosp_permissions(), indent=2))
        self.permission_group_web.close_driver()
        self.permission_web.close_driver()
        
        u.log_result("Groups and permission extracted to: " 
                     + BaseFrameworkAndroidManifest.LOCAL_GROUPS + " and " 
                     + BaseFrameworkAndroidManifest.LOCAL_PERMISSION + ".")
    
    def get_aosp_permissions(self) -> dict:
        """Extract android declared permissions from webpage.

        Returns:
            dict: Containing "androidPermission_list" with a list of 
                permissions.
        """
        permission_list = []
        with alive_bar(len(self.permission_list)) as bar:
            for i in self._get_aosp_permissions():
                permission_list.append(i.to_dict())
                bar()
                
        if len(permission_list) == 0:
            u.log_warning("Empty list.", "No permissions were extracted from " 
                          + "Android AndroidManifest.xml.")
        else:
            u.log_normal(
                "%d permissions were extracted." % len(permission_list)
            )
                
        return {"androidPermission_list": permission_list}

    def _get_aosp_permissions(self) -> AndroidPermission:
        """Finds Android permissions on AndroidManifest.

        Yields:
            AndroidPermission: Next AndroidPermission found.
        """
        for p in self.permission_list:
            # Data extraction
            permission_name = p.attrib[
                u.get_tag_containing("name", p.attrib.keys())
            ]
            protection_level = p.attrib[
                u.get_tag_containing("protectionLevel", p.attrib.keys())
            ]
            added_in_api = self.permission_web.get_added_in_api_level(
                permission_name
            )            
            group = None
            if u.get_tag_containing("permissionGroup", p.attrib.keys()):
                # Get previous declared group on Manifest.
                while p.tag != "permission-group":
                    p = p.getprevious()
                    
                group_name = p.attrib[
                    u.get_tag_containing("name", p.attrib.keys())
                ]
                group = AndroidPermissionGroup(group_name, "")
            
            # Exceptions
            if "WRITE_EXTERNAL_STORAGE" in permission_name:
                group = AndroidPermissionGroup(
                    "android.permission-group.STORAGE", 
                    ""
                )
            if "BLUETHOOT" in permission_name:
                group = None
            if "UWB" in permission_name:
                group = None
            if "NEARBY" in permission_name:
                group = None
            if "GET_ACCOUNTS" in permission_name:
                group = None
            
            yield AndroidPermission(permission_name, 
                                    protection_level, 
                                    None, 
                                    None, 
                                    added_in_api, 
                                    group)
            
    def get_aosp_permission_groups(self) -> dict:
        """Extract Android declared groups from webpage.

        Returns:
            dict: Containing "androidPermissionGroup_list" with a list of 
                permissions.
        """
        group_list = []
        with alive_bar(len(self.permission_group_list)) as bar:
            for i in self._get_aosp_permission_groups():
                group_list.append(i.to_dict())
                bar()
                
        if len(group_list) == 0:
            u.log_warning("Empty list.", 
                          "No permission groups were extracted from Android " 
                          + "AndroidManifest.xml.")
        else:
            u.log_normal(
                "%d permission groups were extracted." % len(group_list)
            )
                
        return {"androidPermissionGroup_list": group_list}
                
    def _get_aosp_permission_groups(self) -> AndroidPermissionGroup:
        """Finds Android permission groups on AndroidManifest.

        Yields:
            AndroidPermissionGroup: Next AndroidPermissionGroup found.
        """
        for g in self.permission_group_list:
            # Data extraction
            group_name = g.attrib[
                u.get_tag_containing("name", g.attrib.keys())
            ]
            added_in_api = self.permission_group_web.get_added_in_api_level(
                group_name
            )
            
            yield AndroidPermissionGroup(group_name, added_in_api)