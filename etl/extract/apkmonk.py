from selenium.webdriver.common.by import By

from etl.extract.live_source import WebSource

from common.util import Util as u


class Apkmonk(WebSource):
    """Represents Apkmonk source.
    """
    
    BASE_URL = "https://www.apkmonk.com/"
    QUERY_URL = "https://www.apkmonk.com/ssearch?q={}"
    APP_PAGE = "https://www.apkmonk.com/app/{}/"
    NAME = "Apkmonk"
    
    def __init__(self) -> None:
        """Creates an Apkmonk object.
        """
        super().__init__()
        
    def find_app(self, package: str) -> str:
        """Search in website for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        u.log_normal("Finding app " + package + " on Apkmonk website...")
        
        # Load website
        url = Apkmonk.QUERY_URL.format(package)
        super()._load_content_page(url)
        
        # Find content
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        link_list = [elem.get_attribute("href") for elem in link_elements]
        link_list = [link for link in link_list if link]
        link_list = [l for l in link_list if "app" == l.split("/")[-3]]
        
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
        u.log_normal("Downloading app " + package + " from Apkmonk website...")
        
        # Get app page
        url = Apkmonk.APP_PAGE.format(package)
        super()._load_content_page(url)
        
        # Extract download link
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        download_links = [e.get_attribute("href") for e in link_elements]
        download_links = [l for l in download_links if l]
        download_links = [l for l in download_links if "download-app" in l]
        
        # Cloudfare detection
        if len(download_links) == 0:
            u.log_error("Cloudfare.", "Detected as bot.")
            self.driver.close()
            return None
        
        # Download app
        filename = super()._download_file_page(download_links[0])
        if not filename:
            u.log_error("File not found.", "Downloading %s error." 
                        % download_links[0])
            self.driver.close()
            return None
        
        u.log_result(Apkmonk.DOWNLOAD_DIR_REL + filename + " downloaded.")
        
        return Apkmonk.DOWNLOAD_DIR_REL + filename
        