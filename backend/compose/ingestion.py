import os
import uuid
import uuid
import threading
from typing import Dict, Any, Tuple
from tkinter import messagebox
from backend.db import deck_repository
from backend.config import app_config

def _get_reader_for_file(file_path: str):
    """Returns the appropriate reader class based on file extension."""
    if file_path.endswith('.xlsx'):
        from backend.anki.input.reader.excel_input_reader import ExcelInputReader
        return ExcelInputReader
    elif file_path.endswith('.csv'):
        from backend.anki.input.reader.csv_input_reader import CSVInputReader
        return CSVInputReader
    elif file_path.startswith('http'):
        from backend.anki.input.reader.gsheet_input_reader import GSheetInputReader
        return GSheetInputReader
    raise ValueError("Unsupported input format")

def run_ingestion(gen_config: dict, fld_mapping: dict, on_success: callable, on_error: callable):
    """
    Runs the ingestion pipeline in a background thread.
    - Creates deck in DECKS
    - Maps fields to DECK_FIELDS
    - Creates dynamic table
    - Batch inserts data from file
    - Generates audio (TODO)
    """
    def task():
        try:
            # 1. Generate UUID for table name
            table_name = str(uuid.uuid4()).replace("-", "") + "_deck"
            
            # 2. Insert into DECKS
            deck_name = gen_config["deck_name"]
            deck_id = deck_repository.create_deck(deck_name, table_name)
            
            # 3. Prepare fields mapping
            # fields dict has key as field_name (e.g. 'expression'), value has 'name' (header) and 'template_field_id'
            fields_for_db = []
            dynamic_columns = []
            header_to_field = {} # Maps Excel header -> dynamic column name (which is the template field name)
            
            for field_name, f_data in fld_mapping["fields"].items():
                fields_for_db.append({
                    "template_field_id": f_data["template_field_id"],
                    "mapped_header": f_data["name"],
                    "audio_generated": f_data.get("generate_audio_file", False)
                })
                
                dynamic_columns.append({
                    "name": field_name,
                    "audio_generated": f_data.get("generate_audio_file", False)
                })
                
                header_to_field[f_data["name"]] = field_name
            
            # 4. Insert into DECK_FIELDS
            deck_repository.add_deck_fields(deck_id, fields_for_db)
            
            # 5. Create Dynamic Table
            deck_repository.create_dynamic_table(table_name, dynamic_columns)
            
            # 6. Read Data using direct extraction
            file_path = gen_config["input_file_path"]
            input_type = gen_config["input_type"]
            sheets_list = gen_config.get("sheets_list", [])
            data_rows = []
            
            if input_type == "csv":
                import csv
                import requests
                if file_path.startswith("http"):
                    response = requests.get(file_path)
                    response.raise_for_status()
                    reader = csv.DictReader(response.text.splitlines())
                    for row in reader:
                        data_rows.append(row)
                else:
                    with open(file_path, newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            data_rows.append(row)
            else:
                import openpyxl
                import io
                import requests
                
                if input_type == "gsheet" or file_path.startswith("http"):
                    response = requests.get(file_path)
                    response.raise_for_status()
                    wb = openpyxl.load_workbook(filename=io.BytesIO(response.content), data_only=True, read_only=True)
                else:
                    wb = openpyxl.load_workbook(filename=file_path, data_only=True, read_only=True)
                    
                target_sheets = sheets_list if sheets_list else wb.sheetnames
                
                for sheet_name in target_sheets:
                    if sheet_name in wb.sheetnames:
                        ws = wb[sheet_name]
                        rows_iter = ws.iter_rows(values_only=True)
                        headers = next(rows_iter, None)
                        if headers:
                            headers = [str(h).strip() if h is not None else "" for h in headers]
                            for row in rows_iter:
                                row_dict = {}
                                for idx, val in enumerate(row):
                                    if idx < len(headers):
                                        row_dict[headers[idx]] = str(val) if val is not None else ""
                                data_rows.append(row_dict)
                wb.close()
            
            # 7. Batch insert data to dynamic table
            # Extract values based on mapped headers
            insert_rows = []
            col_names = [col["name"] for col in dynamic_columns]
            
            for row_dict in data_rows:
                # row_dict keys are the actual spreadsheet headers
                row_tuple = []
                for col_name in col_names:
                    # find the header that maps to this col_name
                    target_header = next((h for h, f in header_to_field.items() if f == col_name), None)
                    val = row_dict.get(target_header, "")
                    row_tuple.append(str(val))
                insert_rows.append(tuple(row_tuple))
                
            deck_repository.batch_insert_data(table_name, col_names, insert_rows)
            
            # 8. Audio generation
            audio_cols = [col["name"] for col in dynamic_columns if col["audio_generated"]]
            if audio_cols:
                # Create media folder
                from backend.config import app_config
                work_dir = app_config.get_work_dir()
                media_dir = os.path.join(work_dir, table_name, "media")
                os.makedirs(media_dir, exist_ok=True)
                
                from backend.speech import speech
                from uuid import uuid4
                from datetime import datetime
                
                # Fetch all rows to process audio
                # Fetching the newly inserted rows by ID
                for batch in deck_repository.fetch_data_batch(table_name, 100):
                    updates = {col: [] for col in audio_cols}
                    for row in batch:
                        row_id = row["id"]
                        for col in audio_cols:
                            text_val = row.get(col, "")
                            if text_val:
                                prefix = str(uuid4().hex)
                                suffix = datetime.now().strftime('%Y%m%d%H%M%S')
                                filename = f"{prefix}{suffix}.mp3"
                                
                                # Generate speech
                                speech.text_to_speech(text_val, filename, audio_folder_path=media_dir)
                                
                                # Add to updates list
                                updates[col].append((filename, row_id))
                    
                    # Batch update for this batch
                    for col, update_list in updates.items():
                        if update_list:
                            deck_repository.batch_update_audio(table_name, f"{col}_$", update_list)
            
            # 9. Return success with the deck config needed for export
            export_context = {
                "deck_id": deck_id,
                "table_name": table_name,
                "deck_name": deck_name,
                "template_id": gen_config["template_id"]
            }
            
            # We don't need to pass the media directory to the export anymore,
            # because the media directory is fixed as work_dir/table_name/media
            
            on_success(export_context)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            on_error(str(e))
            
    threading.Thread(target=task, daemon=True).start()
