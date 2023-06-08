from common.domain.element import Element
from common.domain.permission_group import PermissionGroup
from common.domain.rank import Rank


class Permission(Element):
    """Represents a permission.
    """
    
    def __init__(self, 
                 name: str = None, 
                 protection_level: str = None, 
                 declared_group_list: list[PermissionGroup] = None,
                 rank_list: list[Rank] = None,
                 dict: dict = None) -> None:
        """Creates a permission.

        Args:
            name (str, optional): Name of the permission. Defaults to None.
            group (PermissionGroup, optional): Permission assigned to group. 
                Defaults to None.
            protection_level (str, optional): Protection level of the 
                permission. Defaults to None.
            declared_group_list (list[PermissionGroup], optional): Permission 
                assigned to groups. Defaults to None.
            rank_list (list[Rank], optional): List of ranks assigned to 
                permission. Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.name = dict["name"]
            self.protection_level = dict["protection_level"]
            
            grps = dict["declared_group_list"]
            if grps:
                g = [PermissionGroup(dict=g["PermissionGroup"]) for g in grps]
                self.declared_group_list = g
            else:
                self.declared_group_list = None
                
            rank_list = dict["rank_list"]
            if rank_list:
                ranks = [Rank(dict=rank["Rank"]) for rank in rank_list]
                self.rank_list = ranks
            else:
                self.rank_list = None
        else: 
            self.name = name
            self.protection_level = protection_level
            self.declared_group_list = declared_group_list
            self.rank_list = rank_list
        
    def to_dict(self) -> dict:
        """Creates a dict representing the permission data.

        Returns:
            dict: Data.
        """
        if self.declared_group_list:
            declared_grp_list = [g.to_dict() for g in self.declared_group_list]
        else:
            declared_grp_list = None
            
        if self.rank_list:
            rank_list = [rank.to_dict() for rank in self.rank_list]
        else:
            rank_list = None
        
        data = {
            "name": self.name,
            "protection_level": self.protection_level,
            "declared_group_list": declared_grp_list,
            "rank_list": rank_list
            }
        
        return {"Permission": data}