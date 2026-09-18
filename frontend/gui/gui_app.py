import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import yaml
import os
import threading
from backend.compose.deck_composer import DeckComposer
from frontend.gui.template_registry import get_template_by_name

from frontend.gui.tabs.general_tab import GeneralTab
from frontend.gui.tabs.fields_tab import FieldsTab

class AnkiComposerGUI(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly", title="Anki Composer", size=(800, 700))
        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Tab 1: General & Input
        self.tab_general = GeneralTab(self.notebook, on_next_step=self.on_general_next, padding=10)
        self.notebook.add(self.tab_general, text="1. General & Input")

        # Tab 2: Map Fields
        self.tab_fields = FieldsTab(self.notebook, on_generate_request=self.on_generate_request, padding=10)
        self.notebook.add(self.tab_fields, text="2. Map Fields", state="disabled")

    def on_general_next(self, template_name: str):
        headers = self.tab_general.get_headers()
        self.tab_fields.rebuild_fields(template_name, headers)
        self.notebook.tab(1, state="normal")
        self.notebook.select(1)

    def on_generate_request(self):
        gen_config = self.tab_general.get_config()
        fld_mapping = self.tab_fields.get_fields_mapping()
        
        # Validation across tabs
        if fld_mapping["audio_requested"] and not gen_config["disable_audio_generation"]:
            media_folder = gen_config["media_folder_path"]
            if not media_folder:
                messagebox.showerror("Validation Error", "Audio generation is requested, but Media Folder Path is empty in the General tab.")
                return
            if not os.path.isdir(media_folder):
                messagebox.showerror("Validation Error", f"Media folder does not exist:\n{media_folder}")
                return

        desc = self._build_descriptor_dict(gen_config, fld_mapping)
        self._execute_generation(desc)

    def _build_descriptor_dict(self, gen_config: dict, fld_mapping: dict) -> dict:
        deck_name_id = gen_config["deck_name"].lower().replace(" ", "-")
        if not deck_name_id:
            deck_name_id = "default-deck"
            
        template = get_template_by_name(gen_config["template_name"])
        
        desc = {
            "version": "1.0",
            "decks": {
                deck_name_id: {
                    "deck_name": gen_config["deck_name"],
                    "input": {
                        "type": gen_config["input_type"],
                        "file_path": gen_config["input_file_path"]
                    },
                    "fields": fld_mapping["fields"],
                    "front_template": {
                        "value": template.front_template if template else ""
                    },
                    "back_template": {
                        "value": template.back_template if template else ""
                    },
                    "output": {
                        "folder_path": gen_config["output_folder_path"],
                        "filename": gen_config["output_filename"]
                    }
                }
            }
        }
        
        if gen_config["sheets_list"]:
            desc["decks"][deck_name_id]["input"]["sheets"] = gen_config["sheets_list"]
            
        if gen_config["media_folder_path"]:
            desc["decks"][deck_name_id]["media_folder_path"] = gen_config["media_folder_path"]
            
        if gen_config["disable_audio_generation"]:
            desc["decks"][deck_name_id]["disable_audio_generation"] = True
            
        return desc

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
                    messagebox.showerror("Error", f"An error occurred:\n{e}")
                        
            threading.Thread(target=run_generation, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to prepare descriptor:\n{e}")

def run():
    app = AnkiComposerGUI()
    app.mainloop()

if __name__ == "__main__":
    run()
