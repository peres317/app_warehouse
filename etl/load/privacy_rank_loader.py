from etl.load.mysql_connector import MysqlConnector
from etl.load._rank_loader import _RankLoader
from etl.load.score_loader import ScoreLoader

from common.domain.privacy_rank import PrivacyRank


class PrivacyRankLoader:
    """Load an AppPermission to warehouse.
    """
    
    def __init__(self) -> None:
        """Creates a privacy rank loader.
        """
        self.mysql_conn = MysqlConnector()
        
    def load_privacy_rank(self, privacy_rank: PrivacyRank) -> dict:
        """Loads privacy rank on database.

        Args:
            privacy_rank (PrivacyRank): PrivacyRank to load.

        Returns:
            dict: {privacy_rank_name, row_count}
                Name of the privacy_rank.
                Number of rows added (1 if loaded succesfully).
        """
        # Loads privacy_rank data if is not already on database
        result = self.download_privacy_rank(privacy_rank.name)
        if result:
            result = {"privacy_rank_name": privacy_rank.name, 
                      "row_count": 0}
        else:
            result = self.mysql_conn.upload_data(
                "INSERT INTO privacy_rank VALUES " 
                + "(%(name)s, %(source)s, %(timestamp)s);", 
                {"name": privacy_rank.name,
                "source": privacy_rank.source,
                "timestamp": privacy_rank.timestamp})
            result = {"privacy_rank_name": privacy_rank.name, 
                      "row_count": result["row_count"]}
        
        # Loads third tables data
        if privacy_rank.permission_ranks_list:
            rank_loader = _RankLoader()
            for rank in privacy_rank.permission_ranks_list:
                rank_loader.load_rank(rank)

        if privacy_rank.app_scores_list:
            score_loader = ScoreLoader()
            for score in privacy_rank.app_scores_list:
                score_loader.load_score(score)
        
        return result
    
    def download_privacy_rank(self, name: str) -> dict:
        """Downloads a privacy_rank from database.

        Args:
            name (str): Id of the privacy rank to download.

        Returns:
            dict: {privacy_rank_name, PrivacyRank}
        """
        # Downloads privacy rank data
        result = self.mysql_conn.download_data_by_id(
            "SELECT * FROM privacy_rank WHERE privacy_rank_name = %(name)s", 
            {"name": name})
        
        # Downloads privacy rank data from third objects
        ranks_loader = _RankLoader()
        ranks = ranks_loader.download_ranks_rank(name)
        
        scores_loader = ScoreLoader()
        scores = scores_loader.download_scores_rank(name)
        
        if result:
            return {"privacy_rank_name": name, 
                    "PrivacyRank": PrivacyRank(*result, ranks, scores)}
                
        return None