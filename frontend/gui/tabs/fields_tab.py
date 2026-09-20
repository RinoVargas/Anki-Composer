import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from frontend.gui.template_registry import get_template_by_name

class FieldsTab(ttk.Frame):
    def __init__(self, master, on_generate_request, on_export_request, **kwargs):
        super().__init__(master, **kwargs)
        self.on_generate_request = on_generate_request
        self.on_export_request = on_export_request
        self.fields = []  # Will hold tuples of (field_id, template_field_id, var_name, var_audio)
        self._build_ui()

    def _build_ui(self):
        self.fields_container = ttk.Frame(self)
        self.fields_container.pack(fill=BOTH, expand=True)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=X, pady=20)
        
        ttk.Button(btn_frame, text="Generate Deck", bootstyle=SUCCESS, command=self._on_generate).pack(side=LEFT, padx=10)
        
        self.btn_export = ttk.Button(btn_frame, text="Exportar Deck", bootstyle=INFO, command=self._on_export, state="disabled")
        self.btn_export.pack(side=LEFT, padx=10)

    def rebuild_fields(self, template_id: int, headers: list[str]):
        for widget in self.fields_container.winfo_children():
            widget.destroy()
            
        self.fields.clear()
        
        from backend.db import template_repository
        template = template_repository.get_template_by_id(template_id)
        
        if not template:
            return
            
        ttk.Label(self.fields_container, text=f"Map columns for template: {template.name}", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        for field_def in template.fields:
            row_frame = ttk.Frame(self.fields_container)
            row_frame.pack(fill=X, pady=5)
            
            ttk.Label(row_frame, text=f"{field_def['label']}:", width=20).pack(side=LEFT, padx=5)
            
            var_name = ttk.StringVar()
            cb_field = ttk.Combobox(row_frame, textvariable=var_name, values=headers, state="readonly", width=23)
            cb_field.pack(side=LEFT, padx=5)
            
            # Select first if any available to provide default
            if headers:
                # Optional: try to auto-match header to field_def['id'] or just pick the first
                cb_field.current(0)
            
            var_audio = ttk.BooleanVar(value=False)
            if field_def.get("audio_allowed", False):
                ttk.Checkbutton(row_frame, text="Generate Audio", variable=var_audio).pack(side=LEFT, padx=15)
                
            self.fields.append((field_def["id"], field_def.get("template_field_id"), var_name, var_audio))

    def _on_generate(self):
        # Local validation for empty fields
        for (field_id, tpl_field_id, var_name, var_audio) in self.fields:
            fname = var_name.get().strip()
            if not fname:
                messagebox.showerror("Validation Error", f"You must specify a column name for: {field_id}")
                return
        
        # Fire callback
        self.on_generate_request()

    def enable_export(self):
        self.btn_export.configure(state="normal")

    def _on_export(self):
        self.on_export_request()

    def get_fields_mapping(self) -> dict:
        fields_dict = {}
        audio_requested = False
        
        for (field_id, tpl_field_id, var_name, var_audio) in self.fields:
            fname = var_name.get().strip()
            faudio = var_audio.get()
            
            if fname:
                fields_dict[field_id] = {
                    "name": fname,
                    "template_field_id": tpl_field_id
                }
                if faudio:
                    fields_dict[field_id]["generate_audio_file"] = True
                    audio_requested = True
                    
        return {
            "fields": fields_dict,
            "audio_requested": audio_requested
        }
