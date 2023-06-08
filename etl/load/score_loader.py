from etl.load.mysql_connector import MysqlConnector

from common.domain.score import Score


class ScoreLoader:
    """Load an Score to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates an score loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_score(self, score: Score) -> dict:
        """Loads score on database.

        Args:
            score (Score): Score to load.

        Returns:
            dict: {app_hash, privacy_rank_name, row_count}
                app_hash of the app associated to score.
                privacy_rank_name of the score.
                Number of rows added (1 if loaded succesfully).
        """
        result = self.mysql_conn.upload_data(
            "INSERT INTO score VALUES "
            + "(%(score_value)s, %(app_hash)s, %(privacy_rank_name)s);", 
            {"score_value": score.value,
             "app_hash": score.app_hash,
             "privacy_rank_name": score.rank_name})
        
        return {"app_hash": score.app_hash,
                "privacy_rank_name": score.rank_name,
                "row_count": result["row_count"]}
    
    def download_score(self, app_hash: str, 
                       privacy_rank_name: str) -> dict:
        """Downloads a rank from database.

        Args:
            app_hash (str): App hash associated.
            privacy_rank_name (str): Rank associated.

        Returns:
            dict: {app_hash, privacy_rank_name, Score}
        """
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM score WHERE " 
            + "app_hash = %(app_hash)s AND "
            + "privacy_rank_name = %(privacy_rank_name)s", 
            {"app_hash": app_hash,
             "privacy_rank_name": privacy_rank_name})
        
        if result:
            return {"app_hash": app_hash,
                    "privacy_rank_name": privacy_rank_name,
                    "Score": Score(*result)}
                
        return None
    
    def download_scores_rank(self, rank_name: str) -> list[Score]:
        """Downloads a score from database.

        Args:
            rank_name (str): Ranking associated.

        Returns:
            lsit[Score]: clasificaciones de un ranking
        """
        result = self.mysql_conn.download_all(
            "SELECT * FROM score WHERE " 
            + "privacy_rank_name = %(rank_name)s",
            {"rank_name": rank_name}
        )
        
        score_list = [Score(*score) for score in result]
                
        return score_list
    
    def download_scores_app(self, app_hash: str) -> list[Score]:
        """Downloads a score from database.

        Args:
            app_hash (str): App associated.

        Returns:
            lsit[Score]: clasificaciones de un ranking
        """
        result = self.mysql_conn.download_all(
            "SELECT * FROM score WHERE " 
            + "app_hash = %(app_hash)s",
            {"app_hash": app_hash}
        )
        
        score_list = [Score(*score) for score in result]
                
        return score_list