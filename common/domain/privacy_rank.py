from common.domain.element import Element
from common.domain.rank import Rank
from common.domain.score import Score


class PrivacyRank(Element):
    """Represents a rank.
    """
    
    def __init__(self, 
                 name: str = None, 
                 source: str = None,
                 timestamp: str = None,
                 permission_ranks_list: list[Rank] = None,
                 app_scores_list: list[Score] = None,
                 dict: dict = None) -> None:
        """Creates a permission.

        Args:
            name (str, optional): Name of the permission. Defaults to None.
            source (str, optional): Defaults to None.
            timestamp (str, optional): Defaults to None.
            permission_ranks_list (list[Rank], optional): Defaults to None.
            app_scores_list (list[Score], optional): Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.name = dict["name"]
            self.source = dict["source"]
            self.timestamp = dict["timestamp"]
            
            ranks = dict["permission_ranks_list"]
            if ranks:
                r = [Rank(dict=rank["Rank"]) for rank in ranks]
                self.permission_ranks_list = r
            else:
                self.permission_ranks_list = None
                
            scores = dict["app_scores_list"]
            if scores:
                s = [Score(dict=score["Score"]) for score in scores]
                self.app_scores_list = s
            else:
                self.app_scores_list = None
        else: 
            self.name = name
            self.source = source
            self.timestamp = timestamp
            self.permission_ranks_list = permission_ranks_list
            self.app_scores_list = app_scores_list
            
    def find_permission_rank(self, permission_name: str) -> float:
        """Finds permission rank.

        Args:
            permission_name (str): Permission name of the rank we want.

        Returns:
            float: Permission rank. None if it is not found.
        """
        for p in self.permission_ranks_list:
            if p.permission_name == permission_name:
                return p.value
            
        return None
        
    def to_dict(self) -> dict:
        """Creates a dict representing the permission data.

        Returns:
            dict: Data.
        """
        if self.permission_ranks_list:
            ranks = [r.to_dict() for r in self.permission_ranks_list]
        else:
            ranks = None
            
        if self.app_scores_list:
            scores = [s.to_dict() for s in self.app_scores_list]
        else:
            scores = None
        
        data = {
            "name": self.name,
            "source": self.source,
            "timestamp": self.timestamp,
            "permission_ranks_list": ranks,
            "app_scores_list": scores
            }
        
        return {"PrivacyRank": data}