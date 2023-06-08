from etl.load.mysql_connector import MysqlConnector

from common.domain.rank import Rank


class _RankLoader:
    """Load an Rank to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an rank loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_rank(self, rank: Rank) -> dict:
        """Loads score on database.

        Args:
            rank (Rank): Rank to load.

        Returns:
            dict: {permission_name, privacy_rank_name, row_count}
                permission_name of the permission associated to rank.
                privacy_rank_name of the rank.
                Number of rows added (1 if app loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO permission_rank VALUES "
            + "(%(rank_value)s, %(permission_name)s, %(privacy_rank_name)s);", 
            {"rank_value": rank.value,
             "permission_name": rank.permission_name,
             "privacy_rank_name": rank.rank_name})
        
        return {"permission_name": rank.permission_name,
                "privacy_rank_name": rank.rank_name,
                "row_count": result["row_count"]}
    
    def download_rank(self, permission_name: str, 
                       privacy_rank_name: str) -> dict:
        """Downloads a rank from database.

        Args:
            permission_name (str): Permission associated.
            privacy_rank_name (str): Rank associated.

        Returns:
            dict: {permission_name, privacy_rank_name, Rank}
        """
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM permission_rank WHERE " 
            + "permission_name = %(permission_name)s AND "
            + "privacy_rank_name = %(privacy_rank_name)s", 
            {"permission_name": permission_name,
             "privacy_rank_name": privacy_rank_name})
        
        if result:
            return {"permission_name": permission_name,
                    "privacy_rank_name": privacy_rank_name,
                    "Rank": Rank(*result)}
                
        return None
    
    def download_ranks_permission(self, permission_name: str) -> list[Rank]:
        """Downloads a rank from database.

        Args:
            permission_name (str): Permission associated.

        Returns:
            lsit[Rank]: clasificaciones de un permiso
        """
        result = self.mysql_conn.download_all(
            "SELECT * FROM permission_rank WHERE " 
            + "permission_name = %(permission_name)s",
            {"permission_name": permission_name}
        )
        
        rank_list = [Rank(*rank) for rank in result]
                
        return rank_list
    
    def download_ranks_rank(self, rank_name: str) -> list[Rank]:
        """Downloads a rank from database.

        Args:
            rank_name (str): Ranking associated.

        Returns:
            lsit[Rank]: clasificaciones de un ranking
        """
        result = self.mysql_conn.download_all(
            "SELECT * FROM permission_rank WHERE " 
            + "privacy_rank_name = %(rank_name)s",
            {"rank_name": rank_name}
        )
                
        rank_list = [Rank(*rank) for rank in result]
                
        return rank_list