from etl.load.mysql_connector import MysqlConnector

from common.domain.extraction_metadata import ExtractionMetadata


class _ExtractionMetadataLoader:
    """Load an ExtractionMetadata to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an ExtractionMetadata loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_metadata(self, 
                      extraction_metadata: ExtractionMetadata,
                      app_hash: str) -> dict:
        """Loads the extraction metadata on database.

        Args:
            extraction_metadata (ExtractionMetadata): Metadata to load.
            app_hash (str): Metadata belongs to app by hash_app. 

        Returns:
            dict: {id, app_hash, row_count}
                id of the metadata.
                app_hash of the metadata.
                Number of rows added (1 if loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO extraction_metadata VALUES (NULL, %(source)s, " 
            + "%(method)s, %(timestamp)s, %(appHash)s);", 
            {"source": extraction_metadata.source, 
             "method": extraction_metadata.method, 
             "timestamp": extraction_metadata.timestamp,
             "appHash": app_hash})
                
        return result | {"app_hash": app_hash}
    
    def download_metadata(self, id: int, app_hash: str) -> dict:
        """Downloads an ExtractionMetadata from database.

        Args:
            id (int): Id of the metadata to download.

        Returns:
            dict: {id, app_hash, ExtractionMetadata}
        """ 
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM extraction_metadata WHERE " 
            + "id = %(id)s AND app_hash = %(app_hash)s;", 
            {"id": id,
             "app_hash": app_hash})
        
        if result:
            return {"id": id, 
                    "app_hash": app_hash, 
                    "ExtractionMetadata": ExtractionMetadata(*result[1:])}
        
        return None
    
    def download_metadata_app(self, app_hash: str) -> list[ExtractionMetadata]:
        """Downloads a extraction metadata from database.

        Args:
            app_hash (str): App associated.

        Returns:
            lsit[ExtractionMetadata]: Metadata de una app
        """
        result = self.mysql_conn.download_all(
            "SELECT * FROM extraction_metadata WHERE " 
            + "app_hash = %(app_hash)s",
            {"app_hash": app_hash}
        )
        
        meta_lst = [ExtractionMetadata(*metadata[1:-1]) for metadata in result]
                
        return meta_lst