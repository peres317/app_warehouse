from common.domain.element import Element


class Score(Element):
    """Represents a app score.
    """
    
    def __init__(self, 
                 value: float = None,
                 app_hash: str = None, 
                 rank_name: str = None, 
                 dict: dict = None) -> None:
        """Creates a rank.

        Args:
            value (float, optional): Value of score. Defaults to None.
            rank_name (str, optional): Source of the rank. Defaults to None.
            app_hash (str, optional): Hash of the app which 
                belongs to score. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.value = dict["value"]
            self.rank_name = dict["rank_name"]
            self.app_hash = dict["app_hash"]
        else:
            self.value = value
            self.rank_name = rank_name
            self.app_hash = app_hash
        
    def to_dict(self) -> dict:
        """Creates a dict representing the score data.

        Returns:
            dict: Data.
        """
        data = {
            "value": self.value,
            "rank_name": self.rank_name,
            "app_hash": self.app_hash
        }
        
        return {"Score": data}