from common.domain.element import Element

class PermissionGroup(Element):
    """Represents a group of permissions.
    """
    
    def __init__(self, 
                 name: str = None,  
                 dict: dict = None) -> None:
        """Creates a permission group.

        Args:
            name (str, optional): Name of the group. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.name = dict["name"]
        else:
            self.name = name
        
    def to_dict(self) -> dict:
        """Creates a dict representing the permission group data.

        Returns:
            dict: Data.
        """
        data = {
            "name": self.name
        }
        
        return {"PermissionGroup": data}