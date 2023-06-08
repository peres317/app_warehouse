from common.domain.permission_group import PermissionGroup


class AndroidPermissionGroup(PermissionGroup):
    """Represents an android defined group of permissions.
    """
    
    def __init__(self, 
                 name: str = None, 
                 added_in_api_level: str = None, 
                 dict: dict = None) -> None:
        """Creates a permission group.

        Args:
            name (str, optional): Name of the group. Defaults to None.
            added_in_api_level (str, optional): API Level when the group was 
                introduced. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            super().__init__(dict=dict["PermissionGroup"])
            self.added_in_api_level = dict["added_in_api_level"]
        else:
            super().__init__(name)
            self.added_in_api_level = added_in_api_level
        
    def to_dict(self) -> dict:
        """Creates a dict representing the android permission group data.

        Returns:
            dict: Data.
        """
        data = super().to_dict() | {
            "added_in_api_level": self.added_in_api_level
        }
        
        return {"AndroidPermissionGroup": data}