import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import yaml
import os
import threading
from backend.compose.deck_composer import DeckComposer
from frontend.gui.template_registry import get_template_by_name

from frontend.gui.tabs.decks_tab import DecksTab
from frontend.gui.tabs.general_tab import GeneralTab
from frontend.gui.tabs.fields_tab import FieldsTab
from frontend.gui.tabs.export_tab import ExportTab
from backend.config import app_config
from backend.db import database

class AnkiComposerGUI(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly", title="Anki Composer", size=(800, 700))
        self.bind("<Configure>", self._on_window_configure)
        
        if app_config.is_configured():
            try:
                db_path = app_config.get_db_path()
                database.init_db(db_path)
                self._build_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load database:\n{e}")
                self._build_setup_ui()
        else:
            self._build_setup_ui()

    def _on_window_configure(self, event):
        # Prevent floating dropdown menus when window is moved
        if event.widget == self:
            def close_all_comboboxes(widget):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        try:
                            # Explicitly call the native Tcl proc to close the popdown
                            self.tk.call('ttk::combobox::Unpost', child._w)
                        except Exception:
                            pass
                    close_all_comboboxes(child)
            close_all_comboboxes(self)

    def _build_setup_ui(self):
        self.setup_frame = ttk.Frame(self)
        self.setup_frame.pack(fill=BOTH, expand=True)
        
        inner_frame = ttk.Frame(self.setup_frame)
        inner_frame.pack(expand=True)
        
        ttk.Label(inner_frame, text="Welcome to Anki Composer", font=("Helvetica", 18, "bold")).pack(pady=20)
        ttk.Label(inner_frame, text="Please select a workspace directory to initialize the application database.", wraplength=400, justify=CENTER).pack(pady=10)
        
        ttk.Button(inner_frame, text="New Configuration", bootstyle=PRIMARY, command=self._on_new_configuration).pack(pady=20)

    def _on_new_configuration(self):
        folder_path = filedialog.askdirectory(title="Select Workspace Directory")
        if folder_path:
            try:
                db_path = app_config.setup_workspace(folder_path)
                database.init_db(db_path)
                messagebox.showinfo("Success", "Workspace configured successfully!")
                self.setup_frame.destroy()
                self._build_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize workspace:\n{e}")

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Decks
        self.tab_decks = DecksTab(self.notebook, padding=10)
        self.notebook.add(self.tab_decks, text="1. Decks")

        # Tab 2: General & Input
        self.tab_general = GeneralTab(self.notebook, on_next_step=self.on_general_next, padding=10)
        self.notebook.add(self.tab_general, text="2. General & Input")

        # Tab 3: Map Fields
        self.tab_fields = FieldsTab(self.notebook, on_generate_request=self.on_generate_request, on_export_request=self.on_export_step, padding=10)
        self.notebook.add(self.tab_fields, text="3. Map Fields", state="disabled")

        # Tab 4: Export Deck
        self.tab_export = ExportTab(self.notebook, on_export_request=self.on_export_deck, padding=10)
        self.notebook.add(self.tab_export, text="4. Export Deck", state="disabled")
        
        # Check if there are decks available
        from backend.db import deck_repository
        decks = deck_repository.get_all_decks()
        if not decks:
            self.notebook.tab(0, state="disabled")
            self.notebook.select(1)
        else:
            self.notebook.select(0)

    def on_general_next(self, template_id: int):
        headers = self.tab_general.get_headers()
        self.tab_fields.rebuild_fields(template_id, headers)
        self.notebook.tab(2, state="normal")
        self.notebook.select(2)

    def on_generate_request(self):
        gen_config = self.tab_general.get_config()
        fld_mapping = self.tab_fields.get_fields_mapping()
        
        from backend.compose.ingestion import run_ingestion
        
        # Create progress window
        import tkinter as tk
        progress_win = tk.Toplevel(self)
        progress_win.title("Generating Deck")
        progress_win.geometry("400x150")
        progress_win.resizable(False, False)
        progress_win.transient(self)
        progress_win.grab_set() # Block main window
        
        ttk.Label(progress_win, text="Processing data, please wait...", font=("Helvetica", 12)).pack(pady=10)
        
        lbl_status = ttk.Label(progress_win, text="Starting...")
        lbl_status.pack(pady=5)
        
        progress_var = ttk.IntVar(value=0)
        pb = ttk.Progressbar(progress_win, maximum=100, variable=progress_var, mode="determinate", length=300)
        pb.pack(pady=10)
        
        def on_progress(percent, msg):
            # Update UI on main thread
            self.after(0, lambda: progress_var.set(percent))
            self.after(0, lambda: lbl_status.config(text=msg))
        
        def on_success(export_context):
            self.after(0, progress_win.destroy)
            self.export_context = export_context
            self.tab_fields.enable_export()
            
            # Unlock and reload Decks tab
            self.notebook.tab(0, state="normal")
            self.tab_decks.load_decks()
            
            messagebox.showinfo("Success", "Data ingested and processed successfully!")
            
        def on_error(err_msg):
            self.after(0, progress_win.destroy)
            messagebox.showerror("Error", f"Failed to process data:\n{err_msg}")
            
        run_ingestion(gen_config, fld_mapping, on_success, on_error, on_progress)

    def on_export_step(self):
        self.notebook.tab(3, state="normal")
        self.notebook.select(3)

    def on_export_deck(self, output_folder: str, output_filename: str):
        if not hasattr(self, 'export_context'):
            return
            
        from backend.compose.deck_composer import DeckComposer
        from backend.compose.deck_specification import DeckSpecification
        from backend.db import template_repository, deck_repository
        from backend.config import app_config
        import os
        
        template = template_repository.get_template_by_id(self.export_context["template_id"])
        deck_fields = deck_repository.get_deck_fields_mapping(self.export_context["deck_id"])
        
        media_folder_path = os.path.join(app_config.get_work_dir(), self.export_context["table_name"], "media")
        if not os.path.isdir(media_folder_path):
            media_folder_path = None
        
        desc = {
            "version": "1.0",
            "decks": {
                self.export_context["table_name"]: {
                    "deck_name": self.export_context["deck_name"],
                    "table_name": self.export_context["table_name"],
                    "media_folder_path": media_folder_path,
                    "fields": deck_fields,
                    "front_template": {
                        "value": template.front_template if template else ""
                    },
                    "back_template": {
                        "value": template.back_template if template else ""
                    },
                    "output": {
                        "folder_path": output_folder,
                        "filename": output_filename
                    }
                }
            }
        }
        
        self._execute_generation(desc)

    def _execute_generation(self, desc: dict):
        from backend.compose.deck_specification import DeckSpecification
        try:
            def run_generation():
                try:
                    specs = [DeckSpecification(deck_dict) for deck_dict in desc["decks"].values()]
                    composer = DeckComposer(specifications=specs)
                    composer.compose()
                    messagebox.showinfo("Success", "Deck generated successfully!")
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Error", f"An error occurred:\n{e}")
                        
            threading.Thread(target=run_generation, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare descriptor:\n{e}")

def run():
    app = AnkiComposerGUI()
    app.mainloop()

if __name__ == "__main__":
    run()
