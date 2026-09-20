import sqlite3
import os

def init_db(db_path: str):
    """
    Initializes the SQLite database at the specified path.
    If it doesn't exist, it creates the file.
    """
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    # Connects to the database (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor = conn.cursor()
    
    # Tabla DECKS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DECKS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_name VARCHAR(500),
            table_name VARCHAR(50)
        )
    """)
    
    # Tabla DECK_TEMPLATES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DECK_TEMPLATES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            template_name VARCHAR(500),
            front_template TEXT,
            back_template TEXT,
            FOREIGN KEY (deck_id) REFERENCES DECKS(id) ON DELETE CASCADE
        )
    """)
    
    # Tabla TEMPLATE_FIELDS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TEMPLATE_FIELDS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            field_name VARCHAR(100),
            audio_generated BOOLEAN,
            is_identifier BOOLEAN,
            FOREIGN KEY (template_id) REFERENCES DECK_TEMPLATES(id) ON DELETE CASCADE
        )
    """)

    # Tabla DECK_FIELDS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DECK_FIELDS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER,
            template_field_id INTEGER,
            mapped_header VARCHAR(255), 
            audio_generated BOOLEAN,
            FOREIGN KEY (deck_id) REFERENCES DECKS(id) ON DELETE CASCADE,
            FOREIGN KEY (template_field_id) REFERENCES TEMPLATE_FIELDS(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    
    from backend.db import template_repository
    template_repository.seed_default_templates()
