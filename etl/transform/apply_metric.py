from common.domain.app import App
from common.domain.privacy_rank import PrivacyRank
from common.util import Util as u

from etl.extract.tosdr import TosdrApi

from abc import ABC, abstractmethod
from os import path
from pandas import read_csv


class Metric(ABC):
    """Interface that represents a metric.
    """
    
    @abstractmethod
    def set_privacy_rank(self, privacy_rank: PrivacyRank) -> None:
        """Sets the privacy rank.

        Args:
            privacy_rank (PrivacyRank): Privacy rank associated.
        """
        pass
    
    @abstractmethod
    def get_app_hash_list(self) -> list[str]:
        """Returns app hash list of apps with the metric applied.

        Returns:
            list[str]: List of hash.
        """
        pass
    
    @abstractmethod
    def get_app_package_candidates(self) -> list[str]:
        """Returns app package list of apps candidates to apply the metric.

        Returns:
            list[str]: List of package. None if all apps are candidates.
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the privacy rank.

        Returns:
            str: Name of the privacy rank.
        """
        pass
    
    @abstractmethod
    def get_score(self, app: App) -> float:
        """Returns the score of an app.

        Args:
            app (App): App.

        Returns:
            float: Normalized 0-10 score.
        """
        pass

class RPNDroidMetric(Metric):
    """Apply RPNDroid permission rank based metric.
    """
    
    # Based on an app that would use all dangerous permissions
    MAX_POSSIBLE_SCORE = 3.13476425409317
    NAME = "RPNDroid"
    
    def __init__(self) -> None:
        """Creates a RPNDroidMetric object.
        """
        
    def get_app_package_candidates(self) -> list[str]:
        """Returns app package list of apps candidates to apply the metric.

        Returns:
            list[str]: List of package. None if all apps are candidates.
        """
        return None

    def set_privacy_rank(self, privacy_rank: PrivacyRank) -> None:
        """Sets the privacy rank.

        Args:
            privacy_rank (PrivacyRank): Privacy rank associated.
        """
        self.privacy_rank = privacy_rank
        
    def get_app_hash_list(self) -> list[str]:
        """Returns app hash list of apps with the metric applied.

        Returns:
            list[str]: List of hash.
        """
        hash_list = []
        for app in self.privacy_rank.app_scores_list:
            hash_list.append(app.app_hash)
            
        return hash_list
        
    @staticmethod
    def get_name() -> str:
        """Returns the name of the privacy rank.

        Returns:
            str: Name of the privacy rank.
        """
        return RPNDroidMetric.NAME
        
    def get_score(self, app: App) -> float:
        """Apply RPNDroid score to an app.

        Args:
            app (App): App.

        Returns:
            float: Normalized 0-10 score.
        """
        # Apply rank
        score = 0
        for permission in app.uses_permission_list:
            if(permission.protection_level 
               and "dangerous" in permission.protection_level):
                permission_rank = self.privacy_rank.find_permission_rank(
                    permission.name
                )
                
                if permission_rank:
                    score += permission_rank

        return score / RPNDroidMetric.MAX_POSSIBLE_SCORE * 10
    

class TosdrMetric(Metric):
    """Apply Tosdr terms of service based metric.
    """
    
    NAME = "Tosdr"
    
    def __init__(self) -> None:
        """Creates a Tosdr object.
        """
        
    def get_app_package_candidates(self) -> list[str]:
        """Returns app package list of apps candidates to apply the metric.

        Returns:
            list[str]: List of package. None if all apps are candidates.
        """
        return None

    def set_privacy_rank(self, privacy_rank: PrivacyRank) -> None:
        """Sets the privacy rank.

        Args:
            privacy_rank (PrivacyRank): Privacy rank associated.
        """
        self.privacy_rank = privacy_rank
        
    def get_app_hash_list(self) -> list[str]:
        """Returns app hash list of apps with the metric applied.

        Returns:
            list[str]: List of hash.
        """
        hash_list = []
        for app in self.privacy_rank.app_scores_list:
            hash_list.append(app.app_hash)
            
        return hash_list
        
    @staticmethod
    def get_name() -> str:
        """Returns the name of the privacy rank.

        Returns:
            str: Name of the privacy rank.
        """
        return TosdrMetric.NAME
        
    def get_score(self, app: App) -> float:
        """Apply Tosdr score to an app.

        Args:
            app (App): App.

        Returns:
            float: Normalized 0-10 score.
        """
        service_name = app.package
        
        package_parts = app.package.split(".")
        if len(package_parts) > 1:
            service_name = package_parts[1]
        
        return TosdrApi.get_score(service_name)
    
    
class PaperMetric(Metric):
    """Apply privacy metric based on a paper containing the scores.
    """
    
    def __init__(self, name: str, scores_db: str) -> None:
        """Creates a PaperMetric object.

        Args:
            name (str): Name of the privacy rank. Must exist.
            scores_db (str): Filepath of the database with the scores.
        """
        self.name = name
        
        if not path.exists(scores_db):
            u.log_error("File not found.", "%s not found." % scores_db)
            return
        
        # Extract app scores
        self.df = read_csv(scores_db)
        self.scores = self.df["Score"]
        
    def get_app_package_candidates(self) -> list[str]:
        """Returns app package list of apps candidates to apply the metric.

        Returns:
            list[str]: List of package. None if all apps are candidates.
        """ 
        return list(self.df["Package"])
        
    def get_app_hash_list(self) -> list[str]:
        """Returns app hash list of apps with the metric applied.

        Returns:
            list[str]: List of hash.
        """
        hash_list = []
        for app in self.privacy_rank.app_scores_list:
            hash_list.append(app.app_hash)
            
        return hash_list
        
    def set_privacy_rank(self, privacy_rank: PrivacyRank) -> None:
        """Sets the privacy rank.

        Args:
            privacy_rank (PrivacyRank): Privacy rank associated.
        """
        self.privacy_rank = privacy_rank
    
    def get_name(self) -> str:
        """Returns the name of the privacy rank.

        Returns:
            str: Name of the privacy rank.
        """
        return self.name
        
    def get_score(self, app: App) -> float:
        """Apply RPNDroid score to an app.

        Args:
            app (App): App.

        Returns:
            float: Normalized 0-10 score. None if no possible rank.
        """
        # Apply rank
        if app.package in list(self.df["Package"]):
            return self.scores[self.df["Package"] == app.package].values[0]
        
        return None