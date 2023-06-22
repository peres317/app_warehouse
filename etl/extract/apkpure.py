from selenium.webdriver.common.by import By
from os import listdir, remove
import zipfile

from common.util import Util as u

from etl.extract.live_source import WebSource


class APKPure(WebSource):
    """Represents APKPure website.
    """
    
    BASE_URL = "https://m.apkpure.com/es/"
    QUERY_URL = "https://m.apkpure.com/es/search?q={}"
    NAME = "APKPure"
    
    def __init__(self) -> None:
        """Creates an APKPureWeb object
        """
        super().__init__()
        self.result = None
        
    def find_app(self, package: str) -> str:
        """Search in website for "package".

        Args:
            package (str): Package to find.

        Returns:
            str: Package found. None if not found.
        """
        u.log_normal("Finding app " + package + " on APKPure website...")
        
        result = self._find_app_by_name(package)
        if not result:
            self.driver.close()
            u.log_warning("Empty list.", "No package " + package + " found on "
                          + "APKPure website.")
            return None
        
        self.result = result
        package, url = result
        
        u.log_result("Found " + package + " package on APKPure.")
        
        return package
    
    def download_app(self, package: str) -> str:
        """Download app by package. Package must exist on website.

        Args:
            package (str): Package found on website.

        Returns:
            str: File directory
        """
        u.log_normal("Downloading app " + package + " from APKPure website...")
        
        # Get app page
        if self.result:
            package, url = self.result
        else:
            package, url = self._find_app_by_name(package)
        super()._load_content_page(url)
        
        # Extract download link    
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        download_links = [e.get_attribute("href") for e in link_elements]
        download_links = [l for l in download_links if l]
        download_links = [l for l in download_links if "?version=latest" in l]
        if len(download_links) == 0:
            self.driver.close()
            u.log_error("File not found.", "Downloading error.")
            return None
        
        # Download app
        filename = super()._download_file_page(download_links[0])
        if not filename:
            self.driver.close()
            u.log_error("File not found.", "Downloading %s error." 
                        % download_links[0])
            return None
        
        # Si es XAPK hay que extraer la APK
        if ".xapk" in filename:
            with zipfile.ZipFile(APKPure.DOWNLOAD_DIR_REL+filename, 'r') as z:
                z.extract(package + ".apk", APKPure.DOWNLOAD_DIR_REL)
                z.close()
                
            remove(APKPure.DOWNLOAD_DIR_REL+filename)
                
            apk_filename = package + ".apk"
        else:
            apk_filename = filename
        
        u.log_result(APKPure.DOWNLOAD_DIR_REL + apk_filename + " downloaded.")
        
        return APKPure.DOWNLOAD_DIR_REL + apk_filename
    
    def _find_app_by_name(self, name: str) -> tuple[str, str]:
        """Finds app by package.

        Args:
            package (str): App package.

        Returns:
            tuple[str, str]: (package, app_url). None if not found.
        """
        # Load website
        url = APKPure.QUERY_URL.format(name)
        super()._load_content_page(url)
        
        # Return first download result of query
        link_elements = self.driver.find_elements(By.TAG_NAME, "a")
        link_list = [elem.get_attribute("href") for elem in link_elements]
        link_list = [link for link in link_list if link]
        
        # Bulk results
        bulk_links = [link for link in link_list if "?" not in link]
        bulk_links = [link for link in bulk_links if name in link]
        if len(bulk_links) > 0:
            package_found = bulk_links[0].split("/")[-1]
            return (package_found, bulk_links[0] + "/download")
        
        # Fancy results
        fancy_links = [link for link in link_list if "/download" in link]
        fancy_links = [link for link in fancy_links if name in link]
        if len(fancy_links) > 0:
            package_found = fancy_links[0].split("/")[-2]
            return (package_found, fancy_links[0])

        
        return None