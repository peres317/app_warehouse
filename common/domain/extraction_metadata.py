from common.domain.element import Element


class ExtractionMetadata(Element):
    """Represents app extraction method data.
    """
    
    def __init__(self, 
                 source: str = None, 
                 method: str = None, 
                 timestamp: str = None,
                 dict: dict = None) -> None:
        """Creates extraction metadata.

        Args:
            source (str, optional): Source of the app. Defaults to None.
            method (str, optional): Method of extraction. Defaults to None.
            timestamp (str, optional): Timestamp of the extraction with format 
                "%Y-%m-%d %H:%M:%S". Defaults to None.
            dict (dict, optional): Dictionary representing the object (discard 
                other params). Defaults to None.
        """
        if dict:
            self.source = dict["source"]
            self.method = dict["method"]
            self.timestamp = dict["timestamp"]
        else:
            self.source = source
            self.method = method
            self.timestamp = timestamp
        
    def to_dict(self) -> dict:
        """Creates a dict representing the android ExtractionMetadata data.

        Returns:
            dict: Data.
        """
        data = {
            "source": self.source,
            "method": self.method,
            "timestamp": self.timestamp
        }
        
        return {"ExtractionMetadata": data}