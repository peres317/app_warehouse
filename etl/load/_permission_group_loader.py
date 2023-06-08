from etl.load.mysql_connector import MysqlConnector

from common.domain.permission_group import PermissionGroup


class _PermissionGroupLoader:
    """Load an permission group to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an PermissionGroup loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_permission_group(self, 
                              permission_group: PermissionGroup) -> dict:
        """Loads the permission group on database.

        Args:
            permission_group (PermissionGroup): Group to load.

        Returns:
            dict: {permission_group_name, row_count}
                name of the permission group.
                Number of rows added (1 if app loaded succesfully).
        """
        result = self.download_permission_group(permission_group.name)
        if result:
            result = {"permission_group_name": result["permission_group_name"], 
                      "row_count": 0}
        else:
            result = self.mysql_conn.upload_data(
                "INSERT INTO permission_group VALUES (%(name)s);", 
                {"name": permission_group.name})
            result = {"permission_group_name": permission_group.name, 
                      "row_count": result["row_count"]}
                
        return result
    
    def download_permission_group(self, name: str) -> dict:
        """Downloads a permission group from database.

        Args:
            name (str): Id of the permission group.

        Returns:
            dict: {permission_group_name, PermissionGroup}
        """
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM permission_group WHERE " 
            + "permission_group_name = %(name)s", 
            {"name": name})
        if result:
            return {"permission_group_name": name,
                    "PermissionGroup": PermissionGroup(name = result[0])}
        
        return None