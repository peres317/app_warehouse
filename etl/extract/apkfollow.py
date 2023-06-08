from selenium.webdriver.common.by import By

from etl.extract.live_source import WebSource

from common.util import Util as u


class Apkfollow(WebSource):
    """Represents Apkfollow source.
    """
    
    BASE_URL = "https://www.apkfollow.com/"
    QUERY_URL = "https://www.apkfollow.com/search?q={}"
    NAME = "Apkfollow"
    
    def __init__(self) -> None:
        """Creates an Apkfollow object.
        """
        super().__init__()
        
    def find_app(self, package: str) -> str:
        """Search in website for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        u.log_normal("Finding app " + package + " on Apkfollow website...")
        
        # Load website
        url = Apkfollow.QUERY_URL.format(package)
        super()._load_content_page(url)
        
        # Find content
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        link_list = [elem.get_attribute("href") for elem in link_elements]
        link_list = [link for link in link_list if link]
        link_list = [l for l in link_list if "app" == l.split("/")[-4]]
        
        # Return first result
        if len(link_list) > 0:
            return link_list[0].split("/")[-2]
        
        self.driver.close()
        
        return None
    
    def download_app(self, package: str) -> str:
        """Download app by package. Package must exist on website.

        Args:
            package (str): Package found on website.

        Returns:
            str: File directory
        """
        u.log_normal(
            "Downloading app " + package + " from Apkfollow website...")
        
        # Get app page
        url = Apkfollow.QUERY_URL.format(package)
        super()._load_content_page(url)
        
        # Extract app page
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        link_list = [elem.get_attribute("href") for elem in link_elements]
        link_list = [link for link in link_list if link]
        link_list = [l for l in link_list if "app" == l.split("/")[-4]]
        
        # Cloudfare detection
        if len(link_list) == 0:
            u.log_error("Cloudfare.", "Detected as bot.")
            self.driver.close()
            return None
        
        super()._load_content_page(link_list[0])
        
        # Extract download link
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        d_links = [e.get_attribute("href") for e in link_elements]
        d_links = [l for l in d_links if l]
        d_links = [l for l in d_links if "download" == l.split("/")[-3]]
        
        # Cloudfare detection
        if len(d_links) == 0:
            u.log_error("Cloudfare.", "Detected as bot.")
            self.driver.close()
            return None
        
        # Download app
        filename = super()._download_file_page(d_links[0])
        if not filename:
            u.log_error("File not found.", "Downloading %s error." 
                        % d_links[0])
            self.driver.close()
            return None
        
        u.log_result(Apkfollow.DOWNLOAD_DIR_REL + filename + " downloaded.")
        
        return Apkfollow.DOWNLOAD_DIR_REL + filename
        