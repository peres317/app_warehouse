from enum import Enum
import json

from common.domain.element import Element
from common.domain.android_permission import AndroidPermission
from common.domain.android_permission_group import AndroidPermissionGroup
from common.domain.app import App
from common.domain.permission import Permission
from common.domain.extraction_metadata import ExtractionMetadata
from common.domain.permission_group import PermissionGroup
from common.domain.rank import Rank
from common.domain.score import Score
from common.domain.privacy_rank import PrivacyRank


class Type(Enum):
    """Represents all possible tags fond on a json.
    """
    LIST = 1
    ELEMENT = 2


class JSONIngest:
    """Capable object of process an json object.
    """
    
    MAP = {"AndroidPermissionGroup": AndroidPermissionGroup,
           "AndroidPermission": AndroidPermission,
           "App": App,
           "ExtractionMetadata": ExtractionMetadata,
           "PermissionGroup": PermissionGroup,
           "Permission": Permission,
           "PrivacyRank": PrivacyRank,
           "Rank": Rank,
           "Score": Score}
    
    def __init__(self, json_string: str) -> None:
        """Creates a json ingest object from json data passed.

        Args:
            json (str): Data.
        """
        self.data = json.loads(json_string)
        
    def extract_data_from_json(self) -> list[Element]:
        """Extract all elements contained in the json.

        Returns:
            list[Element]: extracted elements.
        """
        element_list = []
        for tag in self.data:
            tag_type = self._parse_tag(tag)
            if tag_type == Type.LIST:
                for element in self.data[tag]:
                    element_list.append(
                        self._extract_element(element)
                    )
            if tag_type == Type.ELEMENT:
                element_list.append(
                    self._extract_element({tag: self.data[tag]})
                )
        
        return element_list
    
    def _extract_element(self, element_dictionary: dict) -> Element:
        """Extract data of an element.

        Args:
            element_dictionary (dict): Dictionary containing the data of 
                element.

        Returns:
            Element: extracted element.
        """
        element_tag = list(element_dictionary.keys())[0]
        return self.MAP[element_tag](dict=element_dictionary[element_tag])
    
    @staticmethod
    def _parse_tag(tag: str) -> Type:
        """Detects type of tag.

        Args:
            tag (str): Tag.

        Returns:
            Type: type of tag.
        """
        if '_' in tag:
            return Type.LIST
        else:
            return Type.ELEMENT