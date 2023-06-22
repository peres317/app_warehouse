from pyandrozoo import pyAndroZoo
import gzip
from alive_progress import alive_bar
from random import random
import json

from common.util import Util as u


class Androzoo:
    """Represents Androzoo source.
    """
    
    CONFIG_FILE = "data/config.json"
    NUM_APPS = 22086095
    NAME = "Androzoo"
    
    def __init__(self) -> None:
        """Creates a Androzoo object.
        """
        self.API_KEY = None
        self.INDEX_FILE = None
        try:
            with open(Androzoo.CONFIG_FILE, '+r', encoding="utf8") as config:
                azoo_data = json.loads(config.read())["ANDROZOO"]
                self.API_KEY = azoo_data["API_KEY"]
                self.INDEX_FILE = azoo_data["INDEX_FILE"]
        except:
            pass
        
        if not self.API_KEY:
            u.log_error("File not found.", "Androzoo api key not found.")
            
    def get_name(self) -> str:
        """Return the name of the source.

        Returns:
            str: Source name.
        """
        return Androzoo.NAME
            
    def download_apps(self, app_hash_list: list[str]) -> None:
        """Download apps contained in app_hash_list 20 by 20.

        Args:
            app_hash_list (list[str]): List of app hashes.
        """
        u.log_normal("Downloading %d apps..." % len(app_hash_list))
        
        # TODO: call with no app_hash from database (prevent duplication)
        androzoo = pyAndroZoo(self.API_KEY)
        
        # Prepare to download apps 20 by 20
        lists = []
        last_i = 0
        for i in range(len(app_hash_list) // 20):
            lists.append(app_hash_list[(5*i):((5*i+20))])
            last_i = i
        lists.append(app_hash_list[(5*last_i):])
        
        # Download apps
        with alive_bar(len(lists)) as bar:
            for i in self._get_apks(androzoo, lists):
                bar()
        
        u.log_result("Downloaded %d apps." % len(app_hash_list))
        
    def _get_apks(self, androzoo: pyAndroZoo, lists: list[list[str]]) -> None:
        """Download all apps contained in lists from androzoo.

        Args:
            androzoo (pyAndroZoo): Androzoo client.
            lists (list[list[str]]): List of lists of app hashes.
        """
        for list in lists:
            androzoo.get(list) # TODO: pyAndroZoo modded to download in data and timeout added
            yield
        
    def get_n_random_hash(self, n_hash: int) -> list[str]:
        """Select n_hash random from index file.

        Args:
            n_hash (int): Number of apps to select. Function will select n_apps
                or less but a close number.

        Returns:
            list[str]: List of hashes.
        """
        u.log_normal("Finding %d random app hashes..." % n_hash)
        
        # Prevent from not selecting any app when small amount
        n_apps = n_hash
        if n_hash < 10:
            n_apps = 10
        
        selected_hash_list = []
        with alive_bar(n_hash) as bar:
            c = 0
            for i in self._select_random_apps(n_apps):
                c += 1
                selected_hash_list.append(i)
                
                bar()
                
                # Prevent from selecting more than should
                if c >= n_hash:
                    break
                
        u.log_result("%d app hashes found." % len(selected_hash_list))
        
        return selected_hash_list
    
    def get_n_random_hash_by_package(self, n_hash: int,
                                     package_list: list[str]) -> list[str]:
        """Select n_hash random from index file.

        Args:
            n_hash (int): Number of apps to select. Function will select n_apps
                or less but a close number.
            package_list (list[str]): Packages allowed to be downloaded.

        Returns:
            list[str]: List of hashes.
        """
        u.log_normal("Finding %d app hashes by package..." % n_hash)
        
        selected_hash_list = []
        with alive_bar(n_hash) as bar:
            c = 0
            for i in self._select_random_apps_by_package(n_hash, package_list):
                c += 1
                selected_hash_list.append(i)
                
                bar()
                
                # Prevent from selecting more than should
                if c >= n_hash:
                    break
                
        u.log_result("%d app hashes found by package." 
                     % len(selected_hash_list))
        
        return selected_hash_list
    
    def _select_random_apps(self, n_apps: int) -> str:
        """Select n_app random app hashes from index file.

        Args:
            n_apps (int): Number of apps to select. Function will select n_apps
                or less but a close number.

        Returns:
            str: Hash of app selected.

        Yields:
            Iterator[str]: Hash of app selected.
        """
        # Probability of select an app
        p_select = n_apps / Androzoo.NUM_APPS
        
        with gzip.open(self.INDEX_FILE, 'r') as index:
            apps_selected = 0
            header = True
            for app in index:
                # Skip header line
                if header:
                    header = False
                    continue
                
                # Select app
                if random() < p_select:
                    apps_selected += 1
                    yield app.decode("utf-8").split(",")[0]

                    if apps_selected >= n_apps:
                        break
                    
    def _select_random_apps_by_package(self, n_apps: int, 
                                       package_list: list[str]) -> str:
        """Select n_app random app hashes from index file. Apps package must be
        inside package_list. It could select less than n_app.

        Args:
            n_apps (int): Number of apps to select. Function will select n_apps
                or less but a close number.
            package_list (list[str]): Packages allowed to be downloaded.

        Returns:
            str: Hash of app selected.

        Yields:
            Iterator[str]: Hash of app selected.
        """
        with gzip.open(self.INDEX_FILE, 'r') as index:
            apps_selected = 0
            header = True
            for app in index:
                # Skip header line
                if header:
                    header = False
                    continue
                
                # Select app
                file_row = app.decode("utf-8").split(",")
                if file_row[5][1:-1] in package_list:
                    apps_selected += 1
                    yield file_row[0]

                    if apps_selected >= n_apps:
                        break