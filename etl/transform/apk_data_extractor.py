from selenium import webdriver
from lxml.etree import XML
from androguard.core.bytecodes.apk import APK
import hashlib
import json

from common.domain.app import App
from common.domain.permission import Permission
from common.domain.permission_group import PermissionGroup
from common.domain.extraction_metadata import ExtractionMetadata
from common.util import Util as u

from etl.extract.play_store import CategoryFinder
from etl.extract.google import ProtectionLevel


class ApkDataExtractor:
    """Represents an object capable of extract data from .apk.
    """
    
    def __init__(self, path_to_apk: str, 
                 metadata: ExtractionMetadata = None) -> None:
        """Creates an ApkDataExtractor object.

        Args:
            path_to_apk (str): Location of the .apk.
            metadata (ExtractionMetadata, optional): Metadata of the extraction
                of the app. Defaults to None.
        """
        self.path_to_apk = path_to_apk
        self.apk = APK(path_to_apk)
        self.manifest_xml = XML(self.apk.get_android_manifest_axml().get_xml())
        self.extraction_metadata = metadata
        self.app = None
        
    def get_app(self, driver: webdriver.Firefox = None) -> App:
        """Converts the data into an App object.

        Args:
            driver (webdriver.Firefox, optional): Browser. Defaults to None.

        Returns:
            App: app containing all possible data extracted.
        """ 
        if self.app:
            return self.app
        
        hash = hashlib.sha256(open(self.path_to_apk, "rb").read()).hexdigest()
        package = self.apk.get_package()
        version_code = int(self.apk.get_androidversion_code())
        version_name = self.apk.get_androidversion_name()
        min_sdk = self.apk.get_min_sdk_version()
        min_sdk = int(min_sdk) if min_sdk else None
        target_sdk = self.apk.get_target_sdk_version()
        target_sdk = int(target_sdk) if target_sdk else None
        max_sdk = self.apk.get_max_sdk_version()
        max_sdk = int(max_sdk) if max_sdk else None
        category = CategoryFinder().get_app_category(package, driver)
        use_per_l = self._get_app_uses_permission()
        defines_permission_list = self._get_permission_definition()
        defines_group_list = self._get_permission_group_definition()
             
        self.app = App(hash, package, version_code, version_name, min_sdk, 
                   target_sdk, max_sdk, category, use_per_l, 
                   defines_permission_list, defines_group_list, 
                   [self.extraction_metadata])
        
        return self.app
     
    def _get_app_uses_permission(self) -> list[Permission]:
        """Extract permissions used by app.

        Returns:
            list[Permission]: List of permissions used by app.
        """
        app_permission_list = []
        for name in self.apk.get_requested_permissions():
            app_permission_list.append(Permission(name))
        
        return app_permission_list
    
    def _get_permission_group_definition(self) -> list[PermissionGroup]:
        """Extract permission groups declared by app

        Returns:
            list[PermissionGroup]: List of permission groups declared by app.
        """
        grp_names = []
        for g in self.manifest_xml.findall("permission-group"):
            grp_names.append(g.get(u.get_tag_containing("name", g.keys())))
        
        return [PermissionGroup(name) for name in grp_names]
    
    def _get_permission_definition(self) -> list[Permission]:
        """Extract permissions defined by app.

        Returns:
            list[Permission]: List of permissions defined by app.
        """
        permission_list = []
        for p in self.manifest_xml.findall("permission"):
            # Extracting permission defined data
            name = p.get(u.get_tag_containing("name", p.keys()))
            plevel_tag = u.get_tag_containing("protectionLevel", p.keys())
            if plevel_tag:
                raw_p_level = p.get(plevel_tag)
                try:
                    protection_level = ProtectionLevel.to_str(raw_p_level)
                except:
                    u.log_error("Parse.", "Could not parse protection level.")
                    protection_level = raw_p_level
            else:
                protection_level = None
            pgrp_tag = u.get_tag_containing("permissionGroup", p.keys())
            if pgrp_tag:
                group_list = [PermissionGroup(p.get(pgrp_tag))]
            else:
                group_list = None
            
            permission_list.append(
                Permission(name, protection_level, group_list)
            )
        
        return permission_list
        
    def to_json(self) -> str:
        """Get a json containing all app data.

        Returns:
            str: Json containing all app data.
        """
        return json.dumps(self.get_app().to_dict())#, indent=2)