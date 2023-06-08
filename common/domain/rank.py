from common.domain.element import Element


class Rank(Element):
    """Represents a permission rank.
    """
    
    def __init__(self, 
                 value: float = None, 
                 permission_name: str = None, 
                 rank_name: str = None, 
                 dict: dict = None) -> None:
        """Creates a rank.

        Args:
            value (float, optional): Value of score. Defaults to None.
            rank_name (str, optional): Source of the rank. Defaults to None.
            permission_name (str, optional): Name of the permission which 
                belongs to rank. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.value = dict["value"]
            self.rank_name = dict["rank_name"]
            self.permission_name = dict["permission_name"]
        else:
            self.value = value
            self.rank_name = rank_name
            self.permission_name = permission_name
        
    def to_dict(self) -> dict:
        """Creates a dict representing the score data.

        Returns:
            dict: Data.
        """
        data = {
            "value": self.value,
            "rank_name": self.rank_name,
            "permission_name": self.permission_name
        }
        
        return {"Rank": data}