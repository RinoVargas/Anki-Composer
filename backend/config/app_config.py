import json
from pathlib import Path
import os

CONFIG_DIR_NAME = ".anki_composer"
CONFIG_FILE_NAME = "app.json"
DB_FILE_NAME = "anki_composer.db"

def _get_config_path() -> Path:
    home = Path.home()
    return home / CONFIG_DIR_NAME / CONFIG_FILE_NAME

def is_configured() -> bool:
    return _get_config_path().is_file()

def setup_workspace(workspace_dir: str) -> str:
    """
    Saves the config file to the home directory pointing to the DB in workspace_dir.
    Returns the absolute path of the newly configured DB.
    """
    config_path = _get_config_path()
    config_dir = config_path.parent
    
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        
    db_path = os.path.join(workspace_dir, DB_FILE_NAME)
    
    config_data = {
        "work_dir": workspace_dir
    }
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
        
    return db_path

def get_work_dir() -> str:
    config_path = _get_config_path()
    if not config_path.is_file():
        raise FileNotFoundError("Application is not configured.")
        
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        
    work_dir = config_data.get("work_dir")
    if not work_dir:
        raise ValueError("work_dir property is missing in configuration.")
    return work_dir

def get_db_path() -> str:
    return os.path.join(get_work_dir(), DB_FILE_NAME)
