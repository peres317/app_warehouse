from etl.load.mysql_connector import MysqlConnector
from etl.load._permission_group_loader import _PermissionGroupLoader
from etl.load._app_defines_group_loader import _AppDefinesGroupLoader
from etl.load._permission_loader import _PermissionLoader
from etl.load._app_defines_permission_loader import _AppDefinesPermissionLoader
from etl.load._app_uses_permission_loader import _AppUsesPermissionLoader
from etl.load._extraction_metadata_loader import _ExtractionMetadataLoader
from etl.load.score_loader import ScoreLoader

from common.domain.app import App


class AppLoader:
    """Load an App to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an app loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_app(self, app: App) -> dict:
        """Loads app on database.

        Args:
            app (App): App to load.

        Returns:
            dict: {hash, row_count}
                Hash of the app.
                Number of rows added (1 if app loaded succesfully else 0).
        """
        result = self.download_app(app.hash)
        if not result:
            result = self.mysql_conn.upload_data("INSERT INTO app VALUES "
                            + "(%(hash)s, %(package)s, %(version_code)s, " 
                            + "%(version_name)s, %(min_sdk)s, "
                            + "%(target_sdk)s, %(max_sdk)s, %(category)s);", 
                            {"hash": app.hash, 
                            "package": app.package, 
                            "version_code": app.version_code, 
                            "version_name": app.version_name, 
                            "min_sdk": app.min_sdk_version, 
                            "target_sdk": app.target_sdk_version, 
                            "max_sdk": app.max_sdk_version, 
                            "category": app.category})
            result = {"hash": app.hash, "row_count": result["row_count"]}
        else:
            result = {"hash": app.hash, "row_count": 0}

        # Defines group list
        if app.defines_group_list:
            group_loader = _PermissionGroupLoader()
            b_load = _AppDefinesGroupLoader()
            for group in app.defines_group_list:
                g_result = group_loader.load_permission_group(group)
                b_load.bind_group(app.hash, g_result["permission_group_name"])

        # Defines permission list
        if app.defines_permission_list:
            permission_loader = _PermissionLoader()
            b_load = _AppDefinesPermissionLoader()
            for perm in app.defines_permission_list:
                p_result = permission_loader.load_permission(perm, app.hash)
                b_load.bind_permission(app.hash, p_result["permission_name"])
                
        # Uses permission list
        if app.uses_permission_list:
            permission_loader = _PermissionLoader()
            b_load = _AppUsesPermissionLoader()
            for perm in app.uses_permission_list:
                p_result = permission_loader.load_permission(perm, app.hash)
                b_load.bind_permission(app.hash, p_result["permission_name"])

        # Extraction metadata list
        if app.extraction_metadata_list:
            metadata_loader = _ExtractionMetadataLoader()
            for meta in app.extraction_metadata_list:
                metadata_loader.load_metadata(meta, app.hash)

        # Score list
        if app.score_list:
            score_loader = ScoreLoader()
            for score in app.score_list:
                score_loader.load_score(score)

        return {"hash": app.hash, "row_count": result["row_count"]}
    
    def download_app_hash_list(self) -> list[str]:
        """Downloads a list of all app hash on the database.

        Returns:
            list[str]: Hash of each app.
        """
        result = self.mysql_conn.download_all(
            "SELECT hash FROM app;"
        )
        hash_list = [hash for (hash,) in result]
        
        return hash_list
    
    def download_app_hash_list_by_package(self, package: str) -> list[str]:
        """Downloads a list of all app hash on the database.
        
        Args:
            package (str): Package of app.

        Returns:
            list[str]: Hash of each app.
        """
        result = self.mysql_conn.download_all(
            "SELECT hash FROM app WHERE package = %(package)s;",
            {"package": package}
        )
        hash_list = [hash for (hash,) in result]
        
        return hash_list
    
    def download_last_app(self, package: str) -> App:
        """Finds last app that matches package.

        Args:
            package (str): Package of app.

        Returns:
            App: App. None if not found.
        """
        package_alike = [
            package,
            "%." + package + ".%",
            "%." + package,
            package + ".%",
            "%" + package + "%"
        ]
        
        for package in package_alike:
            result = self.mysql_conn.download_data_by_id(
                "SELECT hash FROM app WHERE package LIKE %(package)s " 
                + "ORDER BY version_code DESC LIMIT 1;",
                {"package": package}
            )
            if result:
                break
        
        if result:
            app_hash = result[0]
            return self.download_app(app_hash)
        
        return None
    
    def download_app(self, hash: str) -> App:
        """Downloads an app from database.

        Args:
            hash (str): Hash of the app to download.

        Returns:
            App: App downloaded. None if app doesn't exist.
        """
        result = self.mysql_conn.download_data_by_id("SELECT * FROM app WHERE "
                                       + "hash = %(hash)s", {"hash": hash})
        
        # Uses permission
        u_perms = _AppUsesPermissionLoader().download_bind_permission(hash)
        
        # Defines permission
        d_perms = _AppDefinesPermissionLoader().download_bind_permission(hash)
        
        # Defines group
        def_grp_list = _AppDefinesGroupLoader().download_bind_group_app(hash)
        
        # Extraction metadata
        e_meta_list = _ExtractionMetadataLoader().download_metadata_app(hash)
        
        # Score list
        score_list = ScoreLoader().download_scores_app(hash)
        
        if result:
            return App(*result, 
                       u_perms, 
                       d_perms, 
                       def_grp_list, 
                       e_meta_list, 
                       score_list)
                
        return None