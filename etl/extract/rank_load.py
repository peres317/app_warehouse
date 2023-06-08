from time import time
from datetime import datetime
from pandas import read_csv
from os import path

from common.domain.privacy_rank import PrivacyRank
from common.domain.rank import Rank
from common.util import Util as u


class RPNDroidRankExtractor:
    """Extracts RPNDroid rank from Javier Crespo's csv.
    """

    RANK_NAME = "RPNDroid"
    RANK_SOURCE = "https://ieeexplore.ieee.org/document/9513992"
    DATA_FILE = "data/referencePermissionsGroupsScores.csv"
    
    def __init__(self) -> None:
        """Creates a RPNDroidRankExtractor object.
        """      
        if not path.exists(RPNDroidRankExtractor.DATA_FILE):
            u.log_error("File not found.", 
                        "data/referencePermissionsGroupsScores.csv not found.")
            return
        
        # Extract ranks
        df = read_csv(RPNDroidRankExtractor.DATA_FILE)
        df = df.drop(columns=["Group"])
        permission_ranks_list = []
        for permission_name in df["Name"]:
            rank_value = df["Score"][df["Name"] == permission_name].values[0]
            permission_ranks_list.append(
                Rank(rank_value, 
                     permission_name, 
                     RPNDroidRankExtractor.RANK_NAME)
            )
        
        t = time()
        timestamp = datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
        self.privacy_rank = PrivacyRank(
            "RPNDroid", 
            "https://ieeexplore.ieee.org/document/9513992",
            timestamp,
            permission_ranks_list)
        
    def get_privacy_rank(self) -> PrivacyRank:
        """Returns RPNDroid privacy rank.

        Returns:
            PrivacyRank: RPNDroid privacy rank.
        """
        return self.privacy_rank