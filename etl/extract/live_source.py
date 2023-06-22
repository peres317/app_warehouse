from __future__ import annotations
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Lock
from os import listdir
import time
import requests
import json

from common.util import Util as u


class LiveSource(ABC):
    """Interface of a live source.
    """
    
    DOWNLOAD_DIR = None
    DOWNLOAD_DIR_REL = "data/app_downloads/"
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the source name.

        Returns:
            str: Source name.
        """
        pass
        
    @abstractmethod
    def find_app(self, package: str) -> str:
        """Search in source for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        pass
    
    @abstractmethod
    def download_app(self, package: str) -> str:
        """Download app by package. Package must exist on source.

        Args:
            package (str): Package found on source.

        Returns:
            str: File directory
        """
        pass
    
    @abstractmethod
    def is_alive(self) -> bool:
        """Check if the source is alive.

        Returns:
            bool: True if it is alive else False.
        """
        pass
    
    
class WebSource(LiveSource):
    """Represents a website live source.
    """
    
    SLEEP_TIME = 1
    TIMEOUT = 5
    BIG_TIMEOUT = 600
    NAME = None
    BASE_URL = None
    CONFIG_FILE = "data/config.json"
    
    def __init__(self) -> None:
        """Creates a WebSource object. When download finish closes the browser.
        """
        try:
            with open(WebSource.CONFIG_FILE, '+r', encoding="utf8") as config:
                path = json.loads(config.read())["ABSOLUTE_PATH_OF_WAREHOUSE"]
                LiveSource.DOWNLOAD_DIR = path + LiveSource.DOWNLOAD_DIR_REL
        except:
            pass
        
         # Prepare the browser to download files
        opt = webdriver.FirefoxOptions()
        opt.set_preference("browser.download.folderList", 2)
        opt.set_preference("browser.download.manager.showWhenStarting", False)
        opt.set_preference("browser.download.dir", LiveSource.DOWNLOAD_DIR)
        opt.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                           "application/vnd.android.package-archive")
        opt.set_preference("browser.download.manager.quitBehavior", 2)
        self.driver = webdriver.Firefox(options=opt)
        self.driver.set_page_load_timeout(5)
        
    def get_name(self) -> str:
        """Returns the source name.

        Returns:
            str: Source name.
        """
        return self.NAME
    
    def is_alive(self) -> bool:
        """Check if the source is alive.

        Returns:
            bool: True if it is alive else False.
        """
        try:
            requests.get(self.BASE_URL)
        except Exception:
            return False
        
        return True
        
    def find_app(self, package: str) -> str:
        """Search in source for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        pass
    
    def download_app(self, package: str) -> str:
        """Download app by package. Package must exist on source.

        Args:
            package (str): Package found on source.

        Returns:
            str: File directory
        """
        pass
        
    def _load_content_page(self, url: str) -> None:
        """Try to load page content by url.

        Args:
            url (str): Url to load.
        """
        # Load webpage
        try:
            self.driver.get(url)
        except Exception:
            return None
        
        # Wait for content
        end_time = time.time() + WebSource.TIMEOUT
        while(len(self.driver.find_elements(By.TAG_NAME, "a")) == 0):
            time.sleep(WebSource.SLEEP_TIME)
            if(time.time() > end_time):
                u.log_error("Timeout.", "Could not load page %s." % url)
                break
            
    def _download_file_page(self, url: str) -> str:
        """Downloads the app by url, wait until download finish.

        Args:
            url (str): Url od direct download to the app.

        Returns:
            str: Filename downloaded.
        """
        filename = None
        
        # Start download
        result = DownloadDir().start_download(url, self.driver)
        if result:
            filename, tmp_filename = result
        else:
            u.log_error("Timeout.", "%s download timeout reached." 
                        % self.get_name())
            return None
        
        # Wait app download
        end_time = time.time() + WebSource.BIG_TIMEOUT
        while tmp_filename in listdir(WebSource.DOWNLOAD_DIR):
            if(time.time() > end_time):
                u.log_error("Timeout.", "%s download timeout reached." 
                            % self.get_name())
                break
            time.sleep(5)
            
        self.driver.close()
        
        return filename
    
class Singleton(type):
    """Singleton design pattern.
    """

    _instances = {}
    _lock = Lock() # Prevents threads to create more than one instance.
    
    def __call__(cls) -> Singleton:
        """Returns or creates the unique instance.

        Returns:
            Singleton: Unique instance of class.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__()
                cls._instances[cls] = instance
            
        return cls._instances[cls]


class DownloadDir(metaclass=Singleton):
    """Represents app download directory.
    """
    
    DOWNLOAD_DIR_REL = "data/app_downloads/"
    TIMEOUT = 5
    
    def __init__(self) -> None:
        self.lock = Lock()
    
    def start_download(self, url: str, driver: webdriver.Firefox) -> str:
        """Get url on driver passed.

        Args:
            url (str): Url to get.
            driver (webdriver.Firefox): Webdriver to use.

        Returns:
            tuple[str, str]: (filename, tmp_file) of started download
        """
        # Sensible code.
        with self.lock:
            # List content of dir
            old_content = listdir(DownloadDir.DOWNLOAD_DIR_REL)
            
            # Start download (only one download can start here)
            try:
                driver.get(url)
            except Exception:
                pass
            
            # Wait for new file appear
            end_time = time.time() + DownloadDir.TIMEOUT
            while True:
                new_content = listdir(DownloadDir.DOWNLOAD_DIR_REL)
                dif = [file for file in new_content if file not in old_content]
                
                # No tmp file (already downloaded?)
                if len(dif) == 1:
                    return (dif[0], "")
                
                # Download on course
                if len(dif) == 2:
                    for i in range(len(dif)):
                        file = dif[i]
                        if file.split(".")[-1] == "part":
                            if i == 0:
                                return (dif[1], dif[0])
                            else:
                                return (dif[0], dif[1])
                
                # Timeout
                if(time.time() > end_time):
                    u.log_error("Timeout.", 
                                "Could not find new file download path.")
                    return None
                
                time.sleep(0.2)