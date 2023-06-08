from common.domain.permission import Permission
from common.domain.permission_group import PermissionGroup
from common.domain.android_permission_group import AndroidPermissionGroup
from common.domain.rank import Rank


class AndroidPermission(Permission):
    """Represents an android defined permission.
    """
    
    def __init__(self, 
                 name: str = None, 
                 protection_level: str = None, 
                 declared_group_list: list[PermissionGroup] = None,
                 rank_list: list[Rank] = None,
                 added_in_api_level: str = None,
                 google_declared_group: AndroidPermissionGroup = None, 
                 dict: dict = None) -> None:
        """Creates a permission.

        Args:
            name (str, optional): Name of the permission. Defaults to None.
            protection_level (str, optional): Protection level of the 
                permission. Defaults to None.
            declared_group_list (list[PermissionGroup], optional): Permission 
                belongs to Group. Defaults to None.
            rank_list (list[Rank], optional): Rank list. Defaults to None.
            added_in_api_level (str, optional): API Level when the permission 
                was introduced. Defaults to None.
            google_declared_group (AndroidPermissionGroup, optional): Group 
                assigned to the permission. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            super().__init__(dict=dict["Permission"])
            self.added_in_api_level = dict["added_in_api_level"]
            
            google_declared_group = dict["google_declared_group"]
            if google_declared_group:
                self.google_declared_group = AndroidPermissionGroup(
                    dict=google_declared_group["AndroidPermissionGroup"]
                    )
            else:
                self.google_declared_group = None
        else:
            super().__init__(name, protection_level, declared_group_list, 
                             rank_list)
            self.added_in_api_level = added_in_api_level
            self.google_declared_group = google_declared_group
        
    def to_dict(self) -> dict:
        """Creates a dict representing the android app permission data.

        Returns:
            dict: Data.
        """
        if self.google_declared_group:
            google_declared_group = self.google_declared_group.to_dict()
        else:
            google_declared_group = None
            
        data = super().to_dict() | {
            "added_in_api_level": self.added_in_api_level,
            "google_declared_group": google_declared_group
        }
        
        return {"AndroidPermission": data} 