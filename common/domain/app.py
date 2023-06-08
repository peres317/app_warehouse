from common.domain.element import Element
from common.domain.permission import Permission
from common.domain.permission_group import PermissionGroup
from common.domain.extraction_metadata import ExtractionMetadata
from common.domain.score import Score


class App(Element):
    """Representation of an App (APK).
    """
    
    def __init__(self, 
                 hash: str = None, 
                 package: str = None, 
                 version_code: int = None, 
                 version_name: str = None, 
                 min_sdk_version: int = None, 
                 target_sdk_version: int = None, 
                 max_sdk_version: int = None, 
                 category: str = None, 
                 use_per_l: list[Permission] = None,
                 defines_permission_list: list[Permission] = None, 
                 defines_group_list: list[PermissionGroup] = None,
                 extraction_metadata_list: list[ExtractionMetadata] = None,
                 score_list: list[Score] = None,
                 dict: dict = None) -> None:
        """Creates an App.

        Args:
            hash (str, optional): SHA256 of the app APK. Defaults to None.
            package (str, optional): Package name of the app. Defaults to None.
            version_code (int, optional): Version code of the app. Defaults to 
                None.
            version_name (str, optional): Version name of the app. Defaults to 
                None.
            min_sdk_version (int, optional): Minimum sdk declared. Defaults to 
                None.
            target_sdk_version (int, optional): Target sdk declared. Defaults 
                to None.
            max_sdk_version (int, optional): Maximum sdk declared. Defaults to 
                None.
            category (str, optional): Category of the app (PlayStore card). 
                Defaults to None.
            uses_permission_list (list[AppPermission], optional): Defaults to 
                None.
            defines_permission_list (list[AppPermission], optional): Defaults 
                to None.
            defines_group_list (list[PermissionGroup], optional): Defaults to 
                None.
            extraction_metadata_list (list[ExtractionMetadata], optional): 
                Defaults to None.
            score_list (list[Score], optional): Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.hash = dict["hash"]
            self.package = dict["package"]
            self.version_code = dict["version_code"]
            self.version_name = dict["version_name"]
            self.min_sdk_version = dict["min_sdk_version"]
            self.target_sdk_version = dict["target_sdk_version"]
            self.max_sdk_version = dict["max_sdk_version"]
            self.category = dict["category"]
            
            use_per_l = dict["uses_permission_list"]
            if use_per_l:
                p = [Permission(dict=p["Permission"]) for p in use_per_l]
                self.uses_permission_list = p
            else:
                self.uses_permission_list = None
                
            def_per_l = dict["defines_permission_list"]
            if def_per_l:
                p = [Permission(dict=p["Permission"]) for p in def_per_l]
                self.defines_permission_list = p
            else:
                self.defines_permission_list = None
                
            grp_l = dict["defines_group_list"]
            if grp_l:
                g = [PermissionGroup(dict=g["PermissionGroup"]) for g in grp_l]
                self.defines_group_list = g
            else:
                self.defines_group_list = None
                
            meta = dict["extraction_metadata_list"]
            if meta:
                metadata_list = [ExtractionMetadata(dict=
                                        m["ExtractionMetadata"]) for m in meta]
                self.extraction_metadata_list = metadata_list
            else:
                self.extraction_metadata_list = None
                
            score = dict["score_list"]
            if score:
                score_list = [Score(dict=s["Score"]) for s in score]
                self.score_list = score_list
            else:
                self.score_list = None
        else:
            self.hash = hash
            self.package = package
            self.version_code = version_code
            self.version_name = version_name
            self.min_sdk_version = min_sdk_version
            self.target_sdk_version = target_sdk_version
            self.max_sdk_version = max_sdk_version
            self.category = category
            self.uses_permission_list = use_per_l
            self.defines_permission_list = defines_permission_list
            self.defines_group_list = defines_group_list
            self.extraction_metadata_list = extraction_metadata_list
            self.score_list = score_list
        
    def to_dict(self) -> dict:
        """Creates a dict representing the app data.

        Returns:
            dict: Data.
        """
        if self.uses_permission_list:
            use_per_l = [p.to_dict() for p in self.uses_permission_list]
        else:
            use_per_l = None
            
        if self.defines_permission_list:
            def_per_l = [p.to_dict() for p in self.defines_permission_list]
        else:
            def_per_l = None
            
        if self.defines_group_list:
            grp_l = [g.to_dict() for g in self.defines_group_list]
        else:
            grp_l = None
            
        if self.extraction_metadata_list:
            meta = [m.to_dict() for m in self.extraction_metadata_list]
        else:
            meta = None
            
        if self.score_list:
            score = [s.to_dict() for s in self.score_list]
        else:
            score = None
        
        data = {"hash": self.hash,
                "package": self.package,
                "version_code": self.version_code,
                "version_name": self.version_name,
                "min_sdk_version": self.min_sdk_version,
                "target_sdk_version": self.target_sdk_version,
                "max_sdk_version": self.max_sdk_version,
                "category": self.category,
                "uses_permission_list": use_per_l,
                "defines_permission_list": def_per_l,
                "defines_group_list": grp_l,
                "extraction_metadata_list": meta,
                "score_list": score
                }
        
        return {"App": data}