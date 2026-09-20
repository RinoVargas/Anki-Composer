import sqlite3
from typing import List, Dict, Any, Generator
from backend.config import app_config

def get_connection():
    return sqlite3.connect(app_config.get_db_path())

def create_deck(deck_name: str, table_name: str) -> int:
    """Inserts a new deck into DECKS and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO DECKS (deck_name, table_name) VALUES (?, ?)",
        (deck_name, table_name)
    )
    deck_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return deck_id

def add_deck_fields(deck_id: int, fields_mapping: List[Dict[str, Any]]):
    """
    Inserts mapping info into DECK_FIELDS.
    fields_mapping items should have: 
        'template_field_id', 'mapped_header', 'audio_generated'
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO DECK_FIELDS (deck_id, template_field_id, mapped_header, audio_generated)
        VALUES (?, ?, ?, ?)
    """
    
    rows = [
        (deck_id, f["template_field_id"], f["mapped_header"], f["audio_generated"])
        for f in fields_mapping
    ]
    
    cursor.executemany(query, rows)
    conn.commit()
    conn.close()

def create_dynamic_table(table_name: str, columns: List[Dict[str, Any]]):
    """
    Creates a dynamic table named `table_name`.
    columns should have: 'name' (str), 'audio_generated' (bool)
    """
    # Base columns
    cols_def = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
    
    for col in columns:
        col_name = col["name"]
        cols_def.append(f'"{col_name}" TEXT')
        if col.get("audio_generated"):
            cols_def.append(f'"{col_name}_$" TEXT')
            
    query = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" (\n" + ",\n".join(cols_def) + "\n)"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()

def batch_insert_data(table_name: str, column_names: List[str], rows: List[tuple]):
    """
    Inserts a batch of rows into the dynamic table.
    """
    if not rows:
        return
        
    placeholders = ", ".join(["?"] * len(column_names))
    cols = ", ".join([f'"{c}"' for c in column_names])
    query = f"INSERT INTO \"{table_name}\" ({cols}) VALUES ({placeholders})"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(query, rows)
    conn.commit()
    conn.close()

def batch_update_audio(table_name: str, audio_column: str, updates: List[tuple]):
    """
    Updates the audio generated path in the dynamic table.
    updates should be a list of tuples: (filename, id)
    """
    if not updates:
        return
        
    query = f"UPDATE \"{table_name}\" SET \"{audio_column}\" = ? WHERE id = ?"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(query, updates)
    conn.commit()
    conn.close()

def fetch_data_batch(table_name: str, batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Yields rows from the dynamic table in batches.
    Returns a list of dicts mapped by column name.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # To easily get dicts
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM \"{table_name}\" ORDER BY id ASC")
    
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        yield [dict(r) for r in rows]
        
    conn.close()

def get_deck_fields_mapping(deck_id: int) -> dict:
    """Returns fields dict suitable for DeckSpecification from DECK_FIELDS"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.field_name, d.mapped_header, d.audio_generated
        FROM DECK_FIELDS d
        JOIN TEMPLATE_FIELDS t ON d.template_field_id = t.id
        WHERE d.deck_id = ?
    ''', (deck_id,))
    rows = cursor.fetchall()
    conn.close()
    
    fields = {}
    for r in rows:
        field_name = r[0]
        mapped_header = r[1]
        fields[field_name] = {
            "name": field_name,
            "generate_audio_file": bool(r[2])
        }
    return fields

def get_all_decks() -> List[Dict[str, Any]]:
    """Returns all decks from the DECKS table."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, deck_name, table_name FROM DECKS ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def count_deck_records(table_name: str) -> int:
    """Counts the total number of records in the dynamic table."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM \"{table_name}\"")
        count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        count = 0
    conn.close()
    return count

def fetch_data_page(table_name: str, limit: int, offset: int) -> List[Dict[str, Any]]:
    """Fetches a specific page of data from the dynamic table."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM \"{table_name}\" ORDER BY id ASC LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [dict(r) for r in rows]
