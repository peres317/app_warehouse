import requests
import json


class TosdrApi:
    """Class representing the TOSDR Api.
    """
    
    REQUEST_URL = "https://api.tosdr.org/search/v4/?query={}"
    RATING_MAP = {
        "A": 0,
        "B": 2.5,
        "C": 5,
        "D": 7.5,
        "E": 10,
        "N/A": None
    }
    
    @staticmethod
    def get_score(service_name: str) -> float:
        """Extracts the rating of a service normalized 0-10. None in case the
        service is not found on source.

        Args:
            service_name (str): Name of the service.

        Returns:
            float: Score obtained for service 0-10. None if not found.
        """
        req = requests.get(TosdrApi.REQUEST_URL.format(service_name))
        data = json.loads(req.text)
        
        if len(data['parameters']['services']) > 0:
            rating = data['parameters']['services'][0]['rating']['letter']
            if rating:
                return TosdrApi.RATING_MAP[rating]
        
        return None
