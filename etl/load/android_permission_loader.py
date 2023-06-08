from common.domain.android_permission import AndroidPermission

from etl.load._permission_loader import _PermissionLoader
from etl.load.android_permission_group_loader import AndroidPermissionGroupLoader


class AndroidPermissionLoader(_PermissionLoader):
    """Load an AndroidPermission to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an Android app permission loader.
        """
        super().__init__()
        
    def load_android_permission(self, 
                android_app_permission: AndroidPermission) -> dict:
        """Loads Android app permission on database.

        Args:
            android_app_permission (AndroidPermission): AndroidPermission 
                to load.

        Returns:
            dict: {permission_name, row_count}
                id of the Android app permission.
                Number of rows added (1 if app loaded succesfully).
        """
        # Load third tables data
        group_name = None
        if android_app_permission.google_declared_group:
            droid_g_loader = AndroidPermissionGroupLoader()
            result_aux = droid_g_loader.load_android_permission_group(
                android_app_permission.google_declared_group
            )
            group_name = result_aux["permission_group_name"]
        
        # Loads AndroidPermission if it is not already on database
        result = self.download_android_permission(android_app_permission.name)
        if result:
            result = {"permission_name": result["permission_name"], 
                      "row_count": 0}
        else:
            super().load_permission(android_app_permission)
            result = self.mysql_conn.upload_data(
                "INSERT INTO android_permission VALUES (%(permission_name)s, "
                + "%(added_in_api)s, %(group_id)s);", 
                {"permission_name": result["permission_name"], 
                "added_in_api": android_app_permission.added_in_api_level,
                "group_id": group_name})
            result = {"permission_name": result["permission_name"], 
                      "row_count": result["row_count"]}
        
        return result
    
    def download_android_permission(self, 
                                name: str) -> dict:
        """Downloads an Android permission from database.

        Args:
            name (str): Id of the Android permission to download.

        Returns:
            dict: {permission_name, AndroidPermission}
        """
        # Download Android permission data
        permission = super().download_permission(name)
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM android_permission WHERE " 
            + "permission_name = %(name)s", 
            {"name": name})
        
        if result:
            # Download Android permission data from third objects
            android_g_loader = AndroidPermissionGroupLoader()
            g = android_g_loader.download_android_permission_group(result[2])
            android_group = None
            if g:
                android_group = g["AndroidPermissionGroup"]
            
            return {
                "permission_name": name, 
                "AndroidPermission" : AndroidPermission(
                    name, 
                    permission["Permission"].protection_level,
                    permission["Permission"].declared_group_list,
                    permission["Permission"].rank_list,
                    result[1],
                    android_group
                )
            }
        
        return None