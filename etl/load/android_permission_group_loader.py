from common.domain.android_permission_group import AndroidPermissionGroup

from etl.load._permission_group_loader import _PermissionGroupLoader

class AndroidPermissionGroupLoader(_PermissionGroupLoader):
    """Load an Android permission group to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an AndroidPermissionGroup loader.
        """
        super().__init__()
        
    def load_android_permission_group(self, 
                                      group: AndroidPermissionGroup) -> dict:
        """Loads the Android permission group on database.

        Args:
            group (AndroidPermissionGroup): Group to load.

        Returns:
            dict: {permission_group_name, row_count}
                name of the permission group.
                Number of rows added (1 if app loaded succesfully).
        """
        result = self.download_android_permission_group(group.name)
        if result:
            result = {"permission_group_name": result["permission_group_name"], 
                      "row_count": 0}
        else:
            result_aux = super().load_permission_group(group)
            result = self.mysql_conn.upload_data(
                "INSERT INTO android_permission_group VALUES (%(name)s," 
                + " %(added_in_api_level)s);", 
                {"name": result_aux["permission_group_name"], 
                "added_in_api_level": group.added_in_api_level})
            result = {"permission_group_name": result["permission_group_name"], 
                      "row_count": result["row_count"]} 
        
        return result
    
    def download_android_permission_group(self, name: str) -> dict:
        """Downloads an Android permission group from database.

        Args:
            name (str): Id of the Android permission group to download.

        Returns:
            dict: {permission_group_name, AndroidPermissionGroup}
        """            
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM android_permission_group WHERE " 
            + "permission_group_name = %(name)s", 
            {"name": name})
        if result:
            return {"permission_group_name": name,
                    "AndroidPermissionGroup": AndroidPermissionGroup(*result)} 
        
        return None