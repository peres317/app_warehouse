import mysql.connector
from mysql.connector.errors import IntegrityError
import json

from common.util import Util as u


class MysqlConnector:
    """Connection to the warehouse database with Loader role.
    """
    
    CONFIG_FILE = "data/config.json"

    def __init__(self) -> None:
        """Creates a connection to the warehouse database. Password should be
        stored in config file.
        """
        host = None
        database = None
        user = None
        password = None
        try:
            with open(self.CONFIG_FILE, '+r') as config:
                mysql_config = json.loads(config.read())["MYSQL"]
                host = mysql_config["host"]
                database = mysql_config["database"]
                user = mysql_config["user"]
                password = mysql_config["password"]
        except:
            pass
        
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()
    
    def upload_data(self, query: str, data: dict) -> dict:
        """Upload data query.

        Args:
            query (str): INSERT query.
            data (dict): Data of the insert query.

        Returns:
            dict: {id, row_count}
                Id of the data uploaded.
                Number of rows added (1 if uploaded succesfully else 0).
        """
        row_count = -1
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
            
            row_count = self.cursor.rowcount
        except Exception:
            u.log_error("Upload fail.", "Could not upload data to database."
                        + " Maybe data already on database?")
            row_count = 0

        return {"id": self.cursor.lastrowid, "row_count": row_count}
    
    def download_data_by_id(self, query: str, data: dict) -> tuple:
        """Download data (1 row only).

        Args:
            query (str): SELECT query.
            data (dict): Data of the select query (commonly only an id).

        Returns:
            tuple: Row result in a tuple or None.
        """
        self.cursor.execute(query, data)
        result = self.cursor.fetchone()
                
        return result
    
    def download_all(self, query: str, data: dict = None) -> list:
        """Downloads all the data result of a query.

        Args:
            query (str): SELECT query.
            data (dict, optional): Data of the select query. Defaults to None.

        Returns:
            list: List with the results.
        """
        self.cursor.execute(query, data)
        result = self.cursor.fetchall()
                
        return result