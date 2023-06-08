from etl.load.mysql_connector import MysqlConnector
from etl.load._permission_loader import _PermissionLoader

from common.domain.permission import Permission


class _AppDefinesPermissionLoader:
    """Binds an app with an used permission.
    """
    
    def __init__(self) -> None:
        """Creates the loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def bind_permission(self, app_hash: str, permission_name: str) -> dict:
        """Loads the bind on database.

        Args:
            app_hash (str): Hash of the application.
            permission_name (str): id of the permission (provided when loading 
                the permission).

        Returns:
            dict: {app_hash, permission_name, row_count}
                Id of the table entry.
                Number of rows added (1 if app loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO app_defines_permission VALUES "
            + "(%(app_hash)s, %(permission_name)s);", 
            {"permission_name": permission_name, 
             "app_hash": app_hash})
                
        return {"app_hash": app_hash,
                "permission_name": permission_name,
                "row_count": result["row_count"]}
    
    def download_bind_permission(self, app_hash: str) -> list[Permission]:
        """Downloads a permission from database.

        Args:
            app_hash (str): App associated.

        Returns:
            lsit[Permission]: Permission de una app
        """
        result = self.mysql_conn.download_all(
            "SELECT permission_name FROM app_defines_permission WHERE " 
            + "app_hash = %(app_hash)s",
            {"app_hash": app_hash}
        )
        
        perm_list = []
        load = _PermissionLoader()
        for name in result:
            perm_list.append(load.download_permission(name[0])["Permission"])
                
        return perm_list