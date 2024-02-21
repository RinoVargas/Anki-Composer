
from os import path

root_path = path.dirname(__file__)
resource_folder_path = path.join(root_path, "resources")
composer_folder_path = path.join(resource_folder_path, "composer")

# Resource files
GSHEET_COMPOSER_FILE_PATH = path.join(composer_folder_path, "gsheet-composer-file.yml")
XLSX_COMPOSER_FILE_PATH = path.join(composer_folder_path, "xlsx-composer-file.yml")
