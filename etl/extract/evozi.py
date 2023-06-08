from selenium.webdriver.common.by import By
import time

from etl.extract.live_source import WebSource

from common.util import Util as u


class Evozi(WebSource):
    """Represents Evozi source.
    """
    
    BASE_URL = "https://apps.evozi.com/apk-downloader/"
    QUERY_URL = "https://apps.evozi.com/apk-downloader/?id={}"
    NAME = "Evozi"
    TIMEOUT = 90
    
    def __init__(self) -> None:
        """Creates an Evozi object.
        """
        super().__init__()
        self.download_url = None
        
    def find_app(self, package: str) -> str:
        """Search in website for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        u.log_normal("Finding app " + package + " on Evozi website...")
        
        # Load website
        url = Evozi.QUERY_URL.format(package)
        super()._load_content_page(url)
        
        # Find Generate Download Link button
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        button = [b for b in buttons if b.text == "Generate DownIoad Link"][0]
        button.click()
        
        # Wait for content
        end_time = time.time() + Evozi.TIMEOUT
        while True:
            time.sleep(Evozi.SLEEP_TIME)
            
            # Find content
            element = self.driver.find_element(By.ID, "apk_info")
            if "3 minutes" not in element.get_attribute("innerHTML"):
                break
            
            if(time.time() > end_time):
                u.log_error("Timeout.", "Expected content do not appear.")
                break
            
        # Package not found
        if "text-success" not in element.get_attribute("innerHTML"):
            u.log_warning("Empty list.", "No package " + package + " found on "
                          + "Evozi website.")
            self.driver.close()
            return None
        
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        links = [elem.get_attribute("href") for elem in link_elements]
        links = [link for link in links if link]
        links = [link for link in links if link[-4:] == ".apk"]
        links = [link for link in links if "chart" not in link]
        
        if len(links) > 0:
            self.download_url = links[0]
        else:
            u.log_warning("Empty list.", "No apk " + package + " found on "
                          + "Evozi website.")
            self.driver.close()
            return None
        
        return package
    
    def download_app(self, package: str) -> str:
        """Download app by package. Package must exist on website.

        Args:
            package (str): Package found on website.

        Returns:
            str: File directory
        """
        u.log_normal(
            "Downloading app " + package + " from Evozi website...")
        
        # Url calculated previously?
        if not self.download_url:
            result = self.find_app(package)
            if not result:
                return None
        
        # Download app
        filename = super()._download_file_page(self.download_url)
        if not filename:
            self.driver.close()
            u.log_error("File not found.", "Downloading %s error." 
                        % self.download_url)
            return None
        
        u.log_result(Evozi.DOWNLOAD_DIR_REL + filename + " downloaded.")
        
        return Evozi.DOWNLOAD_DIR_REL + filename
        