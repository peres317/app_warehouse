from os import path
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
        
from common.util import Util as u


class CategoryFinder:
    """Find all possible categories on Google Play based on web support.
    """
    
    CATEGORIES_URL = ("https://support.google.com/googleplay/"
                      "android-developer/answer/9859673"
                      "?hl=en-419#zippy=%2Capps%2Cgames")
    APP_URL_PREFIX = "https://play.google.com/store/apps/details?id="
    LOCAL_FILE = 'data/play_store_downloads/app_categories.dat'
    SLEEP_TIME = 1
    TIMEOUT = 5
    
    def __init__(self) -> None:
        """Creates a category finder object.
        """
        self.categories = []
        
        if path.exists(CategoryFinder.LOCAL_FILE):            
            self.categories = u.read_list(CategoryFinder.LOCAL_FILE)
            
    def get_app_category(self, package: str, 
                         driver: webdriver.Firefox = None) -> str:
        """Goes to Google Play Store and finds out the app category.

        Args:
            package (str): App.
            driver (webdriver.Firefox, optional): Browser. Defaults to None.

        Returns:
            str: Category of the app.
        """
        # Load app page
        tmp_driver = False
        if not driver:
            driver = webdriver.Firefox()
            tmp_driver = True
            
        driver.get(CategoryFinder.APP_URL_PREFIX + package)
        
        # Wait for content
        end_time = time.time() + self.TIMEOUT
        while(len(driver.find_elements(By.TAG_NAME, "a")) == 0):
            time.sleep(CategoryFinder.SLEEP_TIME)
            if(time.time() > end_time):
                u.log_error("Timeout.", "Could not load page %s." 
                            % CategoryFinder.APP_URL_PREFIX + package)
                break

        # Extract app caregory
        links = driver.find_elements(By.TAG_NAME, "a")
        links = filter(lambda x : x.is_displayed(), links)
        links = map(lambda x : x.get_attribute("href"), links)
        links = [l for l in links if "category" in l]
        
        if tmp_driver:
            driver.close()
        
        category = None
        try:
            category = links[0].split('/')[-1]
        except Exception:
            u.log_warning("Empty list.", "Category not found for package %s." 
                          % package)
        
        return category

    def get_categories(self, local: bool = True) -> list[str]:
        """Returns a list of all categories found.

        Args:
            local (bool, optional): If you want the local stored result. 
                Defaults to True.

        Returns:
            list[str]: List of categories.
        """
        u.log_normal("Finding PlayStore app categories...")
        if local and len(self.categories) > 0:
            u.log_result("%d categories found." % len(self.categories))
            
            return self.categories
        
        # Load categories page
        driver = webdriver.Firefox()
        driver.get(CategoryFinder.CATEGORIES_URL)
        
        # Wait for content
        end_time = time.time() + CategoryFinder.TIMEOUT
        while len(driver.find_elements(By.TAG_NAME, "th")) == 0:
            time.sleep(CategoryFinder.SLEEP_TIME)
            if time.time() > end_time:
                u.log_error("Timeout.", "Could not load page %s." 
                            % CategoryFinder.CATEGORIES_URL)
                break

        # Find table location
        table_header_list = driver.find_elements(By.TAG_NAME, "th")
        for header in table_header_list:
            if header.text == "Category":
                x_location = header.rect['x']

        # Find categories
        categories = []
        table_categories = driver.find_elements(By.TAG_NAME, "td")
        for category in table_categories:
            if category.rect['x'] == x_location:
                categories.append(category.text)
                
        driver.close()

        # Parse category names
        self.categories = list(map(lambda x: x.upper().replace(" ", "_"), 
                                   categories))
        
        u.log_result("%d categories found." % len(self.categories))
        
        # Store categories found
        if len(self.categories) > 0:
            u.write_list(CategoryFinder.LOCAL_FILE, self.categories)

        return self.categories
    

class AppFinder:
    """Represents an play store app finder.
    """
    
    CATEGORY_URL_PREFIX = "https://play.google.com/store/apps/category/"
    LOCAL_FILE = 'data/play_store_downloads/app_packages.dat'
    SLEEP_TIME = 1
    TIMEOUT = 5
    
    def __init__(self) -> None:
        """Creates an app object.
        """
        self.app_packages = []
        if path.exists(AppFinder.LOCAL_FILE):            
            self.app_packages = u.read_list(AppFinder.LOCAL_FILE)
        
    def get_app_candidates(self, local: bool = True) -> list[str]:
        """Returns a list of app packages of the main pages of each category.

        Args:
            local (bool, optional): If you want the local stored result. 
                Defaults to True.

        Returns:
            list[str]: List of packages.
        """
        u.log_normal("Finding PlayStore app candidates...")
        if local and len(self.app_packages) > 0:
            u.log_result("%d apps found." % len(self.app_packages))
            
            return self.app_packages
        
        if not local:
            self.app_packages = []
        
        # Compose urls
        categories = CategoryFinder().get_categories()
        urls = list(map(lambda x: AppFinder.CATEGORY_URL_PREFIX+x, categories))
        urls = zip(urls, categories)
        
        driver = webdriver.Firefox()
        
        for (url, category) in urls:
            # Load web
            driver.get(url)
            
            # Wait for content
            timeout = False
            end_time = time.time() + AppFinder.TIMEOUT
            while not self.links_present(driver):
                time.sleep(AppFinder.SLEEP_TIME)
                if time.time() > end_time:
                    u.log_error("Timeout.", "Could not load page %s." % url)
                    timeout = True
                    break
            if timeout:
                continue
            
            # Get app links
            links = driver.find_elements(By.TAG_NAME, "a")
            links = list(map(lambda x : x.get_attribute("href"), links))
            links = [l for l in links if "details?id=" in l]
            
            # Get app packages
            app_ids = [re.sub('.*id=', '', l) for l in links]
            
            if len(app_ids) == 0:
                u.log_warning("Empty list.", "Category " + category + " does "
                              + "not contain any app on PlayStore.")
            
            self.app_packages += app_ids

        driver.close()
        
        if len(self.app_packages) > 0:
            u.log_result("%d apps found." % len(self.app_packages))
            u.write_list(self.LOCAL_FILE, self.app_packages)
        else:
            u.log_warning("Empty list.", "No candidate apps found on " 
                          + "PlayStore.")

        return self.app_packages
    
    def links_present(self, driver: webdriver) -> bool:
        """Find on web loaded on driver if there is app links present.

        Args:
            driver (webdriver): Webdriver with page loaded.

        Returns:
            bool: True if there are links else False.
        """
        links = driver.find_elements(By.TAG_NAME, "a")
        links = list(map(lambda x : x.get_attribute("href"), links))
        links = [l for l in links if "details?id=" in l]
        
        return len(links) > 0