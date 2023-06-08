from etl.load.mysql_connector import MysqlConnector

from common.domain.permission_group import PermissionGroup


class _AppDefinesGroupLoader:
    """Binds an app with a group of permission.
    """
    
    def __init__(self) -> None:
        """Creates the loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def bind_group(self, app_hash: str, group_name: str) -> dict:
        """Loads the bind on database.

        Args:
            app_hash (str): Hash of the application.
            group_name (str): id of the group (provided when loading the group).

        Returns:
            dict: {permission_group_name, app_hash, row_count}
                Id of the table entry.
                Number of rows added (1 if app loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO app_defines_group VALUES "
            + "(%(group_name)s, %(app_hash)s);", 
            {"group_name": group_name, 
             "app_hash": app_hash})
                
        return {"permission_group_name": group_name, 
                "app_hash": app_hash, 
                "row_count": result["row_count"]}
    
    def download_bind_group_app(self, app_hash: str) -> list[PermissionGroup]:
        """Downloads a permission group from database.

        Args:
            app_hash (str): App associated.

        Returns:
            lsit[PermissionGroup]: PermissionGroup de una app
        """
        result = self.mysql_conn.download_all(
            "SELECT * FROM app_defines_group WHERE " 
            + "app_hash = %(app_hash)s",
            {"app_hash": app_hash}
        )
        
        group_list = [PermissionGroup(group[0]) for group in result]
                
        return group_list