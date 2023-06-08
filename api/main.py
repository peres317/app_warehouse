import sys,os
sys.path.append(os.getcwd())

from controller.controller import LoadController as db
from controller.controller import AdminController as admin

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import json
from threading import Thread, Lock

###########
# THREADS #
###########

# Single threads
aosp_thread = Thread()
app_candidates_thread = Thread()
random_n_download_thread = Thread()
random_n_candidates_thread = Thread()
apply_metrics_thread = Thread()

# Current threads
MAX_LIVE_UPLOAD_THREADS = 2
live_upload_lock: Lock = Lock()
live_upload_threads: list[Thread] = []


##################
# AUTHENTICATION #
##################

# Obtain stored api keys
CONFIG_FILE = "data/config.json"
with open(CONFIG_FILE, '+r') as config:
    data_dict = json.loads(config.read())
    API_KEYS = data_dict["API_ACCESS_KEYS"]
    ADMIN_API_KEYS = data_dict["API_ADMIN_ACCESS_KEYS"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    """Authenticates a user by its api key.

    Args:
        api_key (str, optional): Api key. Defaults to Depends(oauth2_scheme).

    Raises:
        HTTPException: Api key not valid.
    """
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Api key not valid"
        )
        
def api_key_admin_auth(api_key: str = Depends(oauth2_scheme)):
    """Authenticates a admin user by its api key.

    Args:
        api_key (str, optional): Admin api key. Defaults to 
            Depends(oauth2_scheme).

    Raises:
        HTTPException: Api key not valid.
    """
    if api_key not in ADMIN_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin api key not valid"
        )


api = FastAPI(
    docs_url=None, # Disable docs (Swagger UI)
    redoc_url=None) # Disable redoc)
api.add_middleware(HTTPSRedirectMiddleware) # Force HTTPS


#####################
# API FUNCTIONALITY #
#####################

@api.get("/get/app/hash", dependencies=[Depends(api_key_auth)])
async def get_app_by_hash(hash: str) -> dict:   
    """Download an app data by its hash.

    Args:
        hash (str): Hash of app to download.

    Raises:
        HTTPException: App not found.

    Returns:
        dict: Data of the app.
    """
    app_data = db.get_app_by_hash(hash)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
            
    return app_data

@api.get("/get/app/package", dependencies=[Depends(api_key_auth)])
async def get_app_by_package(package: str) -> dict:
    """Download an app data by its package like.

    Args:
        package (str): Package of app to download.

    Raises:
        HTTPException: App not found.

    Returns:
        dict: Data of the app.
    """
    app_data = db.get_app_by_package(package)
    if not app_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
            
    return app_data

@api.post("/post/app/package", dependencies=[Depends(api_key_auth)])
async def upload_app_by_package(req: Request) -> dict:
    """Try to download app by package provided. Only one at once.

    Args:
        req (Request): Request.

    Raises:
        HTTPException: Json body not correct.
        HTTPException: Missing package tag on json.

    Returns:
        dict: {status}
    """
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Json body not correct"
        )
    if not "package" in data.keys():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing package tag"
        )
    
    with live_upload_lock:
        # Update list of threads
        global live_upload_threads
        live_upload_threads = [t for t in live_upload_threads if t.is_alive()]
        
        response = {"status": ""}
        
        if len(live_upload_threads) == MAX_LIVE_UPLOAD_THREADS:
            response["status"] = "busy"
        else:
            thread = Thread(target=db.request_app_upload,
                            args=[data["package"]])
            thread.start()
            
            live_upload_threads.append(thread)
            
            response["status"] = "requested"
                
        return response

@api.get("/post/app/package/status", dependencies=[Depends(api_key_auth)])
async def upload_app_by_package_status() -> dict:
    """Return status of upload app request.

    Returns:
        dict: {n_threads}
    """
    with live_upload_lock:
        # Update list of threads
        global live_upload_threads
        live_upload_threads = [t for t in live_upload_threads if t.is_alive()]

        return {"n_threads": len(live_upload_threads)}
    

###########################
# ADMIN API FUNCTIONALITY #
###########################

@api.post("/admin/post/json", dependencies=[Depends(api_key_admin_auth)])
async def upload_json(req: Request) -> dict:
    """Try to upload provided json.

    Args:
        req (Request): Request.

    Raises:
        HTTPException: Json body not correct.

    Returns:
        dict: {status}
    """
    response = {"startus": "requested"}
    try:
        admin.upload_json(await req.body())
        
        response = {"startus": "successful"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Json body not correct"
        )
                    
    return response

@api.get("/admin/update/aosp", dependencies=[Depends(api_key_admin_auth)])
async def update_aosp_data() -> dict:
    """Request to update aosp data. Ony one at once.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    
    global aosp_thread
    if aosp_thread.is_alive():
        response["status"] = "busy"
    else:
        aosp_thread = Thread(target=admin.update_aosp_data, name="Aosp")
        aosp_thread.start()
            
        response["status"] = "requested"

    return response

@api.get("/admin/update/aosp/status", 
         dependencies=[Depends(api_key_admin_auth)])
async def update_aosp_data_status() -> dict:
    """Return status of aosp data update request.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    if aosp_thread.is_alive():
        response["status"] = "busy"
    else:
        response["status"] = "inactive"

    return response

@api.get("/admin/clean_cache", dependencies=[Depends(api_key_admin_auth)])
async def clean_cache() -> dict:
    """Cleans cache. Be careful when to execute this cad delete in use files.

    Returns:
        dict: {deleted_files}
    """
    return admin.clean_cache()
    
@api.get("/admin/update/app_candidates", 
         dependencies=[Depends(api_key_admin_auth)])
async def update_app_candidates() -> dict:
    """Request to update app candidates. Ony one at once.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    
    global app_candidates_thread
    if app_candidates_thread.is_alive():
        response["status"] = "busy"
    else:
        app_candidates_thread = Thread(target=admin.get_app_candidates, 
                                       name="App candidates")
        app_candidates_thread.start()
            
        response["status"] = "requested"

    return response

@api.get("/admin/update/app_candidates/status", 
         dependencies=[Depends(api_key_admin_auth)])
async def update_app_candidates_status() -> dict:
    """Return status of app candidates update request.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    if app_candidates_thread.is_alive():
        response["status"] = "busy"
    else:
        response["status"] = "inactive"

    return response

@api.get("/admin/get/n_random_apps", 
         dependencies=[Depends(api_key_admin_auth)])
async def get_n_random_apps(n_apps: int) -> dict:
    """Request to download n_apps random apps.

    Args:
        n_apps (int): Number of apps to download.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    
    global random_n_download_thread
    if random_n_download_thread.is_alive():
        response["status"] = "busy"
    else:
        random_n_download_thread = Thread(target=admin.download_random_apps, 
                                          name="Androzoo random download", 
                                          args=[n_apps])
        random_n_download_thread.start()
            
        response["status"] = "requested"

    return response

@api.get("/admin/get/n_random_apps/status", 
         dependencies=[Depends(api_key_admin_auth)])
async def get_n_random_apps_status() -> dict:
    """Return status of n random apps download request.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    if random_n_download_thread.is_alive():
        response["status"] = "busy"
    else:
        response["status"] = "inactive"

    return response

@api.get("/admin/get/n_random_app_candidates", 
         dependencies=[Depends(api_key_admin_auth)])
async def get_n_random_app_candidates(n_apps: int) -> dict:
    """Request to download n_apps app candidates.

    Args:
        n_apps (int): Number of apps to download.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    
    global random_n_candidates_thread
    if random_n_candidates_thread.is_alive():
        response["status"] = "busy"
    else:
        random_n_candidates_thread = Thread(
            target=admin.download_random_apps_from_candidates, 
            name="Androzoo random download", 
            args=[n_apps])
        random_n_candidates_thread.start()
            
        response["status"] = "requested"

    return response

@api.get("/admin/get/n_random_app_candidates/status", 
         dependencies=[Depends(api_key_admin_auth)])
async def get_n_random_app_candidates_status() -> dict:
    """Return status of n random candidate apps download request.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    if random_n_candidates_thread.is_alive():
        response["status"] = "busy"
    else:
        response["status"] = "inactive"

    return response

@api.get("/admin/update/apply_metrics",
         dependencies=[Depends(api_key_admin_auth)])
async def apply_metrics() -> dict:
    """Request to apply score metrics to all apps.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    
    global apply_metrics_thread
    if apply_metrics_thread.is_alive():
        response["status"] = "busy"
    else:
        apply_metrics_thread = Thread(
            target=admin.apply_all_metrics, 
            name="All metrics")
        apply_metrics_thread.start()
            
        response["status"] = "requested"

    return response

@api.get("/admin/update/apply_metrics/status", 
         dependencies=[Depends(api_key_admin_auth)])
async def get_n_random_app_candidates_status() -> dict:
    """Return status of apply score metrics to all apps request.

    Returns:
        dict: {status}
    """
    response = {"status": ""}
    if apply_metrics_thread.is_alive():
        response["status"] = "busy"
    else:
        response["status"] = "inactive"

    return response

if __name__ == '__main__':
    uvicorn.run("api.main:api", port=8000, host='0.0.0.0',
                ssl_keyfile="data/key.pem", ssl_certfile="data/cert.pem")