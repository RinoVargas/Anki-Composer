import sqlite3
from backend.config import app_config
from frontend.gui.template_registry import TEMPLATES, TemplateDefinition

def get_connection():
    return sqlite3.connect(app_config.get_db_path())

def seed_default_templates():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if default template exists
    cursor.execute("SELECT id FROM DECK_TEMPLATES WHERE template_name = ?", ("Default Idioms Template",))
    row = cursor.fetchone()
    
    if not row:
        default_tpl = TEMPLATES[0]
        cursor.execute(
            "INSERT INTO DECK_TEMPLATES (deck_id, template_name, front_template, back_template) VALUES (NULL, ?, ?, ?)",
            (default_tpl.name, default_tpl.front_template, default_tpl.back_template)
        )
        template_id = cursor.lastrowid
        
        for field in default_tpl.fields:
            cursor.execute(
                "INSERT INTO TEMPLATE_FIELDS (template_id, field_name, audio_generated, is_identifier) VALUES (?, ?, ?, ?)",
                (template_id, field["id"], field["audio_allowed"], False)
            )
            
        conn.commit()
    conn.close()

def get_all_templates() -> list[dict]:
    """Returns a list of dictionaries with 'id' and 'name'."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, template_name FROM DECK_TEMPLATES")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def get_template_by_id(template_id: int) -> TemplateDefinition:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, template_name, front_template, back_template FROM DECK_TEMPLATES WHERE id = ?", (template_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    template_name = row[1]
    front_template = row[2]
    back_template = row[3]
    
    cursor.execute("SELECT id, field_name, audio_generated, is_identifier FROM TEMPLATE_FIELDS WHERE template_id = ?", (template_id,))
    fields_rows = cursor.fetchall()
    
    fields = []
    for f in fields_rows:
        fields.append({
            "id": f[1], # field_name
            "template_field_id": f[0], # The DB ID of the TEMPLATE_FIELDS row
            "label": f[1].capitalize(),
            "audio_allowed": bool(f[2])
        })
        
    conn.close()
    
    tpl = TemplateDefinition(
        name=template_name,
        fields=fields,
        front_template=front_template,
        back_template=back_template
    )
    tpl.id = row[0] # Add id property dynamically
    return tpl
