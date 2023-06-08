from etl.load.mysql_connector import MysqlConnector
from etl.load._rank_loader import _RankLoader
from etl.load._permission_group_loader import _PermissionGroupLoader
from etl.load._app_bind_permission_to_group_loader import _AppBindPermissionToGroupLoader

from common.domain.permission import Permission


class _PermissionLoader:
    """Load an AppPermission to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an app permission loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_permission(self, app_permission: Permission, 
                        app_hash: str = None) -> dict:
        """Loads app permission on database.

        Args:
            app_permission (AppPermission): AppPermission to load.
            app_hash (str, optional): When the permission is declared or used
                by an app. Defaults to None.

        Returns:
            dict: {permission_name, row_count}
                Name of the app permission.
                Number of rows added (1 if app loaded succesfully).
        """
        # Load permission data if not already on database
        result = self.download_permission(app_permission.name)
        if result:
            result = {"permission_name": app_permission.name, 
                      "row_count": 0}
        else:
            result = self.mysql_conn.upload_data(
                "INSERT INTO permission VALUES " 
                + "(%(name)s, %(protection_level)s);", 
                {"name": app_permission.name,
                "protection_level": app_permission.protection_level})
            result = {"permission_name": app_permission.name, 
                      "row_count": result["row_count"]}
        
        # Bind app, permission and group
        if app_hash:
            if app_permission.declared_group_list:
                group_loader = _PermissionGroupLoader()
                bind_loader = _AppBindPermissionToGroupLoader()
                
                for group in app_permission.declared_group_list:
                    g_result = group_loader.load_permission_group(group)
                    
                    bind_loader.bind_permission_to_group(
                        app_hash, 
                        result["permission_name"], 
                        g_result["permission_group_name"]) 
        
        # Load third tables data      
        if app_permission.rank_list:
            rank_loader = _RankLoader()
            for rank in app_permission.rank_list:
                rank_loader.load_rank(rank)
        
        return result
    
    def download_permission(self, name: str) -> dict:
        """Downloads an app permission from database.

        Args:
            name (str): Id of the app permission to download.

        Returns:
            dict: {permission_name, Permission}
        """
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM permission WHERE permission_name = %(name)s", 
            {"name": name})
        
        # Download third tables data
        groups_binded_loader = _AppBindPermissionToGroupLoader()
        groups = groups_binded_loader.download_groups_of_permission(name)
        
        ranks_loader = _RankLoader()
        ranks = ranks_loader.download_ranks_permission(name)
        
        if result:
            return {"permission_name": name, 
                    "Permission": Permission(*result, groups, ranks)}
                
        return None