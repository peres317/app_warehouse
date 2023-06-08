from etl.load.mysql_connector import MysqlConnector

from common.domain.permission_group import PermissionGroup


class _AppBindPermissionToGroupLoader:
    """Binds an app permission, a group of permission, a permission.
    """
    
    def __init__(self) -> None:
        """Creates the loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def bind_permission_to_group(self, app_hash: str, permission_name: str, 
                                 group_name: str) -> dict:
        """Loads the bind on database.

        Args:
            app_hash (str): Hash of the application.
            permission_id (str): id of the permission (provided when loading 
                the permission).
            group_id (str): id of the group (provided when loading the group).

        Returns:
            dict: {permission_group_name, permission_name, app_hash, row_count}
                Id of the table entry.
                Number of rows added (1 if app loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO app_bind_permission_to_group VALUES "
            + "(%(group_name)s, %(permission_name)s, "
            + "%(app_hash)s);", 
            {"permission_name": permission_name, 
             "group_name": group_name,
             "app_hash": app_hash})
                
        return {"permission_group_name": group_name, 
                "permission_name": permission_name, 
                "app_hash": app_hash, 
                "row_count": result["row_count"]}
    
    def download_groups_of_permission(self, 
                        permission_name: str) -> list[PermissionGroup]:
        """Downloads all the group names binded to permission.

        Args:
            permission_name (str): Permission name.

        Returns:
            list[PermissionGroup]: Permission groups.
        """
        result = self.mysql_conn.download_all(
            "SELECT permission_group_name FROM app_bind_permission_to_group " 
            + "WHERE permission_name = %(permission_name)s;",
            {"permission_name": permission_name}
        )
        
        group_list = [PermissionGroup(group[0]) for group in result]
        
        return group_list