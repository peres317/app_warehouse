from etl.extract import * # Important first of all due to androzoo
from etl.transform import *
from etl.load import *

from common.domain.extraction_metadata import ExtractionMetadata
from common.domain.score import Score
from common.util import Util as u

from selenium import webdriver
from time import time
from datetime import datetime as date
import os


class LoadController:
    """Controller of the database of the warehouse.
    """
    
    LIVE_SOURCES: list[live_source.LiveSource] = [
        apkpure.APKPure,
        evozi.Evozi,
        apkmonk.Apkmonk,
        apkfollow.Apkfollow
    ]
    
    @staticmethod    
    def get_app_by_hash(hash: str) -> dict:
        """Downloads an app data by its hash.

        Args:
            hash (str): Hash of app to download.

        Returns:
            dict: Data of the app.
        """
        app = app_loader.AppLoader().download_app(hash)
        
        if app:
            u.log_result("%s app downloaded." % app.package)
            return app.to_dict()
        
        return None
    
    @staticmethod    
    def get_app_by_package(package: str) -> dict:
        """Downloads an app data by its package like.

        Args:
            package (str): Package of app to download.

        Returns:
            dict: Data of the app.
        """
        app = app_loader.AppLoader().download_last_app(package)
        
        if app:
            u.log_result("%s app downloaded." % app.package)
            return app.to_dict()
        
        return None
    
    @staticmethod
    def request_app_upload(package: str) -> None:
        """Try to download app by package, parse it and upload it to database.

        Args:
            package (str): App package.
        """
        if len(package) < 1:
            return
        
        apk_dir = None
        for source_obect in LoadController.LIVE_SOURCES:
            source: live_source.LiveSource = source_obect()
            
            if source.is_alive():
                # Find app in source
                package_found = source.find_app(package)
                if not package_found:
                    continue
                
                # Download app from source               
                apk_dir = source.download_app(package_found)
                if apk_dir:
                    break
                
        if not apk_dir:
            return

        # Extract data from app and load to warehouse
        extraction_metadata = ExtractionMetadata(
            source.get_name(),
            "web scraping",
            date.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
        )
        _CommonController.load_app(apk_dir, extraction_metadata)
        
        # Apply metrics
        AdminController.apply_all_metrics()
                
        return


class AdminController:
    """Controller of the admin of the warehouse.
    """
    
    METRICS: list[apply_metric.Metric] = [
            apply_metric.RPNDroidMetric(),
            apply_metric.TosdrMetric(),
            apply_metric.PaperMetric("PTaP privacy impact", 
                                    "data/paper1a.csv"),
            apply_metric.PaperMetric("PTaP threats by review", 
                                    "data/paper1b.csv"),
            apply_metric.PaperMetric("TUDelft intrusiveness", 
                                    "data/paper2.csv")
        ]
    
    @staticmethod
    def apply_all_metrics() -> None:
        """Apply all stored metrics to all stored apps. Prevents 
        recalculations.
        """
        u.log_normal("Applying all metrics...")
        
        # Download all dynamic metrics
        p_r_loader = privacy_rank_loader.PrivacyRankLoader()
        for metric in AdminController.METRICS:
            req = p_r_loader.download_privacy_rank(metric.get_name())
            metric.set_privacy_rank(req["PrivacyRank"])
        
        # Apply all metrics
        c = 0
        s_loader = score_loader.ScoreLoader()
        a_loader = app_loader.AppLoader()
        app_hash_list = app_loader.AppLoader().download_app_hash_list()
        
        for metric in AdminController.METRICS:
            done = metric.get_app_hash_list()
            remaining = [app for app in app_hash_list if app not in done]
            
            if metric.get_app_package_candidates():
                app_candidates = []
                for package in metric.get_app_package_candidates():
                    l = a_loader.download_app_hash_list_by_package(package)
                    app_candidates = app_candidates + l

                remaining = [app for app in remaining if app in app_candidates]
            
            u.log_normal(str(len(remaining)) + " apps remaining with " 
                         + metric.get_name() + " metric.")
            
            for app_hash in remaining:
                app = a_loader.download_app(app_hash)
                score_value = metric.get_score(app)
                
                score = Score(score_value, app_hash, metric.get_name())
                s_loader.load_score(score)
                    
                c += 1
        
        u.log_result("%d scores loaded." % c)
    
    @staticmethod
    def upload_json(json: str) -> None:
        """Try to upload json data to database. Only allow to upload apps, 
        scores and privacy ranks.

        Args:
            json (str): Json formatted data.
        """
        element_list = json_ingest.JSONIngest(json).extract_data_from_json()
        
        # Allowed elements.
        load_map = {
            "<class 'common.domain.privacy_rank.PrivacyRank'>": 
                privacy_rank_loader.PrivacyRankLoader().load_privacy_rank,
            "<class 'common.domain.score.Score'>":
                score_loader.ScoreLoader().load_score,
            "<class 'common.domain.app.App'>":
                app_loader.AppLoader().load_app,
        }
        
        for element in element_list:
            load_map[str(type(element))](element)
            
        return
    
    @staticmethod
    def download_random_apps(n_apps: int) -> None:
        """Feed the warehouse with n_apps apps random.

        Args:
            n_apps (int): Number of apps to upload.
        """
        # Get random app list
        hash_list = androzoo.Androzoo().get_n_random_hash(n_apps)
        
        # Do not download data on database
        database_hash = app_loader.AppLoader().download_app_hash_list()
        hash_list = [h for h in hash_list if h.lower() not in database_hash]
        
        # Download apps
        androzoo.Androzoo().download_apps(hash_list)
        
        # Extract data from apps
        extraction_metadata = ExtractionMetadata(
            androzoo.Androzoo().get_name(),
            "api",
            date.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
        )
        
        driver = webdriver.Firefox()
        for apk_path in os.listdir("data/androzoo_downloads/"):
            apk_path = "data/androzoo_downloads/" + apk_path
            _CommonController.load_app(apk_path, extraction_metadata, driver)
        driver.close()
        
        return
    
    @staticmethod
    def download_random_apps_from_candidates(n_apps: int) -> None:
        """Feed the warehouse with n_apps apps from app candidates.

        Args:
            n_apps (int): Number of apps to upload.
        """
        # Get random app list
        hash_list = androzoo.Androzoo().get_n_random_hash_by_package(
            n_apps, 
            play_store.AppFinder().get_app_candidates(local=True)
        )
        
        # Do not download data on database
        database_hash = app_loader.AppLoader().download_app_hash_list()
        hash_list = [h for h in hash_list if h.lower() not in database_hash]
        
        # Download apps
        androzoo.Androzoo().download_apps(hash_list)
        
        # Extract data from apps
        extraction_metadata = ExtractionMetadata(
            androzoo.Androzoo().get_name(),
            "api",
            date.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')
        )
        
        driver = webdriver.Firefox()
        for apk_path in os.listdir("data/androzoo_downloads/"):
            apk_path = "data/androzoo_downloads/" + apk_path
            _CommonController.load_app(apk_path, extraction_metadata, driver)
        driver.close()
        
        # Apply metrics
        AdminController.apply_all_metrics()
        
        return
    
    @staticmethod
    def get_app_candidates() -> None:
        """Stores in tmp dir app package candidates.
        """
        play_store.AppFinder().get_app_candidates(local=False)
        
        return
    
    @staticmethod
    def update_aosp_data() -> None:
        """Updates all Android permission and groups data from warehouse.
        """
        # Get new data
        google.BaseFrameworkAndroidManifest().download_all_data(local=False)
        
        # Upload data to warehouse
        loader = android_permission_group_loader.AndroidPermissionGroupLoader()
        with open("data/google_downloads/groups.json", "+r", 
                  encoding="utf8") as f:
            data = f.read()
            for group in json_ingest.JSONIngest(data).extract_data_from_json():
                loader.load_android_permission_group(group)
        loader = android_permission_loader.AndroidPermissionLoader()
        with open("data/google_downloads/permission.json", "+r", 
                  encoding="utf8") as f:
            data = f.read()
            for perm in json_ingest.JSONIngest(data).extract_data_from_json():
                loader.load_android_permission(perm)
                
        u.log_result("Aosp data uploaded to database.")
        
        return
    
    @staticmethod
    def clean_cache() -> dict:
        """Deletes all files from tmp directories.
        """
        files = 0
        for path in os.listdir("data/"):
            if path.split("_")[-1] == "downloads":
                for file in os.listdir("data/" + path):
                    files += 1
                    os.remove("data/" + path + "/" +  file)
                    
        return {"deleted_files": files}
    
    
class _CommonController:
    """Common controller functionalities.
    """
    
    @staticmethod
    def load_app(apk_path: str, 
                  extraction_metadata: ExtractionMetadata,
                  driver: webdriver.Firefox = None) -> None:
        """Load app in apk_path to warehouse and delete it.

        Args:
            apk_path (str): Path to app apk.
            extraction_metadata (ExtractionMetadata): Metadata of the 
                extraction.
            driver (webdriver.Firefox, optional): Browser. Defaults to None.
        """
        # Extract data from apk
        app = apk_data_extractor.ApkDataExtractor(
            apk_path, 
            extraction_metadata
        ).get_app(driver)
                
        # Upload app to warehouse
        app_loader.AppLoader().load_app(app)
        
        # Delete apk file
        if os.path.exists(apk_path):
            os.remove(apk_path)
                
        u.log_result("%s app loaded." % app.package)