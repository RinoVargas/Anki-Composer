import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import os
from backend.db import deck_repository
from backend.audio import audio_player
from backend.config import app_config

class DecksTab(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.page_size = 50
        self.current_page = 0
        self.total_records = 0
        self.current_deck = None
        self.current_deck_fields = {}
        
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=BOTH, expand=True)
        
        self.list_view = ttk.Frame(self.main_container)
        self.detail_view = ttk.Frame(self.main_container)
        
        self._build_list_view()
        self._build_detail_view()
        
        self.show_list_view()

    def _build_list_view(self):
        header_frame = ttk.Frame(self.list_view)
        header_frame.pack(fill=X, pady=10)
        ttk.Label(header_frame, text="Generated Decks", font=("Helvetica", 14, "bold")).pack(side=LEFT)
        
        buttons_frame = ttk.Frame(self.list_view)
        buttons_frame.pack(fill=X, pady=5)
        
        btn_refresh = ttk.Button(buttons_frame, text="Refresh", bootstyle=SECONDARY, command=self.load_decks)
        btn_refresh.pack(side=LEFT)
        
        self.btn_view_detail = ttk.Button(buttons_frame, text="Ver Detalle", bootstyle=INFO, command=self._on_view_detail_click, state=DISABLED)
        self.btn_view_detail.pack(side=RIGHT)
        
        self.tree_decks = ttk.Treeview(self.list_view, columns=("id", "deck_name"), show="headings", height=15)
        self.tree_decks.heading("id", text="ID")
        self.tree_decks.heading("deck_name", text="Deck Name")
        
        self.tree_decks.column("id", width=50, anchor=CENTER)
        self.tree_decks.column("deck_name", width=700, anchor=CENTER)
        
        self.tree_decks.pack(fill=BOTH, expand=True, pady=10)
        self.tree_decks.bind("<<TreeviewSelect>>", self._on_deck_select)
        
        self.load_decks()

    def _build_detail_view(self):
        header_frame = ttk.Frame(self.detail_view)
        header_frame.pack(fill=X, pady=10)
        
        ttk.Button(header_frame, text="◀ Back to Decks", bootstyle=SECONDARY, command=self.show_list_view).pack(side=LEFT)
        
        self.lbl_deck_title = ttk.Label(header_frame, text="", font=("Helvetica", 14, "bold"))
        self.lbl_deck_title.pack(side=LEFT, padx=20)
        
        self.tree_records = ttk.Treeview(self.detail_view, show="headings", height=15)
        self.tree_records.pack(fill=BOTH, expand=True, pady=10)
        self.tree_records.bind("<ButtonRelease-1>", self._on_record_click)
        self.tree_records.bind("<Button-2>", self._on_record_right_click)
        self.tree_records.bind("<Button-3>", self._on_record_right_click)
        
        # Pagination controls
        page_frame = ttk.Frame(self.detail_view)
        page_frame.pack(fill=X, pady=5)
        
        self.btn_prev = ttk.Button(page_frame, text="◀ Prev", bootstyle=INFO, command=self._prev_page)
        self.btn_prev.pack(side=LEFT)
        
        self.lbl_page = ttk.Label(page_frame, text="Page 1")
        self.lbl_page.pack(side=LEFT, expand=True)
        
        self.btn_next = ttk.Button(page_frame, text="Next ▶", bootstyle=INFO, command=self._next_page)
        self.btn_next.pack(side=RIGHT)

    def load_decks(self):
        for item in self.tree_decks.get_children():
            self.tree_decks.delete(item)
            
        decks = deck_repository.get_all_decks()
        for deck in decks:
            self.tree_decks.insert("", END, values=(deck["id"], deck["deck_name"]), tags=(deck["table_name"],))

    def show_list_view(self):
        self.detail_view.pack_forget()
        self.list_view.pack(fill=BOTH, expand=True)
        self.current_deck = None
        self.btn_view_detail.config(state=DISABLED)
        # Clear selection so user has to click again
        self.tree_decks.selection_remove(self.tree_decks.selection())
        self.update_idletasks()

    def show_detail_view(self, deck: dict):
        self.current_deck = deck
        self.current_page = 0
        self._hidden_cells = set()
        self._hidden_columns = set()
        self.lbl_deck_title.config(text=deck["deck_name"])
        
        # Setup columns
        self.current_deck_fields = deck_repository.get_deck_fields_mapping(deck["id"])
        
        # Build columns for treeview
        columns = ["id"]
        for field_name in self.current_deck_fields.keys():
            columns.append(field_name)
            
        # Switch frames FIRST so we can measure the treeview width properly
        self.list_view.pack_forget()
        self.detail_view.pack(fill=BOTH, expand=True)
        self.update_idletasks() # Let the UI render the full width treeview container
        
        tree_width = self.tree_records.winfo_width()
        if tree_width < 100:
            tree_width = 800
            
        dynamic_cols_count = len(self.current_deck_fields)
        col_width = (tree_width - 50) // dynamic_cols_count if dynamic_cols_count > 0 else 150
            
        self.tree_records.config(columns=columns)
        self.tree_records.heading("id", text="ID")
        self.tree_records.column("id", width=50, stretch=False, minwidth=50)
        
        for field_name, field_data in self.current_deck_fields.items():
            header_text = field_name.capitalize()
            if field_data.get("generate_audio_file"):
                header_text += " (Audio)"
            self.tree_records.heading(field_name, text=header_text)
            self.tree_records.column(field_name, width=col_width, stretch=True, minwidth=100)
            
        self.total_records = deck_repository.count_deck_records(deck["table_name"])
        self.load_records_page()

    def load_records_page(self):
        self._audio_cache = {}
        self._text_cache = {}
        for item in self.tree_records.get_children():
            self.tree_records.delete(item)
            
        offset = self.current_page * self.page_size
        records = deck_repository.fetch_data_page(self.current_deck["table_name"], self.page_size, offset)
        
        columns = self.tree_records.cget("columns")
        for record in records:
            record_id = str(record["id"])
            values = []
            
            # Store in text_cache
            row_texts = {}
            for col in columns:
                raw_val = record.get(col, "")
                row_texts[col] = raw_val
                
                col_hidden = col in self._hidden_columns
                cell_toggled = (record_id, col) in self._hidden_cells
                is_hidden = (not cell_toggled) if col_hidden else cell_toggled
                
                if is_hidden:
                    values.append("***")
                else:
                    values.append(raw_val)
                
            item_id = self.tree_records.insert("", END, values=values)
            self.tree_records.item(item_id, tags=(record_id,))
            self._text_cache[item_id] = row_texts
            
            item_audios = {}
            for f_name, f_data in self.current_deck_fields.items():
                if f_data.get("generate_audio_file"):
                    audio_val = record.get(f"{f_name}_$")
                    if audio_val:
                        item_audios[f_name] = audio_val
            self._audio_cache[item_id] = item_audios
            
        # Update pagination controls
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        self.lbl_page.config(text=f"Page {self.current_page + 1} of {total_pages}")
        
        self.btn_prev.config(state=NORMAL if self.current_page > 0 else DISABLED)
        self.btn_next.config(state=NORMAL if self.current_page < total_pages - 1 else DISABLED)

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_records_page()

    def _next_page(self):
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_records_page()

    def _on_deck_select(self, event):
        selection = self.tree_decks.selection()
        if selection:
            self.btn_view_detail.config(state=NORMAL)
        else:
            self.btn_view_detail.config(state=DISABLED)

    def _on_view_detail_click(self):
        selection = self.tree_decks.selection()
        if not selection:
            return
            
        item = self.tree_decks.item(selection[0])
        deck = {
            "id": item["values"][0],
            "deck_name": item["values"][1],
            "table_name": item["tags"][0]
        }
        self.show_detail_view(deck)

    def _on_record_click(self, event):
        region = self.tree_records.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        col_id = self.tree_records.identify_column(event.x)
        item_id = self.tree_records.identify_row(event.y)
        
        if not item_id:
            return
            
        col_index = int(col_id.replace('#', '')) - 1
        columns = self.tree_records.cget("columns")
        
        if col_index < len(columns):
            col_name = columns[col_index]
            
            # Check audio cache
            item_audios = getattr(self, '_audio_cache', {}).get(item_id, {})
            audio_file = item_audios.get(col_name)
            
            if audio_file:
                work_dir = app_config.get_work_dir()
                file_path = os.path.join(work_dir, self.current_deck["table_name"], "media", audio_file)
                audio_player.play_audio(file_path)

    def _on_record_right_click(self, event):
        region = self.tree_records.identify_region(event.x, event.y)
        col_id = self.tree_records.identify_column(event.x)
        if not col_id:
            return
            
        col_index = int(col_id.replace('#', '')) - 1
        columns = self.tree_records.cget("columns")
        if col_index >= len(columns):
            return
            
        col_name = columns[col_index]
        
        if region == "heading":
            import tkinter as tk
            menu = tk.Menu(self, tearoff=0)
            
            col_hidden = col_name in self._hidden_columns
            has_toggles = any(c == col_name for r, c in self._hidden_cells)
            
            if col_hidden:
                menu.add_command(label=f"Mostrar columna", command=lambda: self._toggle_column(col_name, False))
                if has_toggles:
                    menu.add_command(label=f"Ocultar columna", command=lambda: self._toggle_column(col_name, True))
            else:
                menu.add_command(label=f"Ocultar columna", command=lambda: self._toggle_column(col_name, True))
                if has_toggles:
                    menu.add_command(label=f"Mostrar columna", command=lambda: self._toggle_column(col_name, False))
            menu.tk_popup(event.x_root, event.y_root)
            return
            
        if region != "cell":
            return
            
        item_id = self.tree_records.identify_row(event.y)
        if not item_id:
            return
            
        record_id = self.tree_records.item(item_id, "tags")[0]
        
        # Toggle visibility state
        state_key = (record_id, col_name)
        if state_key in self._hidden_cells:
            self._hidden_cells.remove(state_key)
        else:
            self._hidden_cells.add(state_key)
            
        # Update visual cell value
        current_values = list(self.tree_records.item(item_id, "values"))
        
        col_hidden = col_name in self._hidden_columns
        cell_toggled = state_key in self._hidden_cells
        is_hidden = (not cell_toggled) if col_hidden else cell_toggled
        
        if is_hidden:
            current_values[col_index] = "***"
        else:
            current_values[col_index] = self._text_cache.get(item_id, {}).get(col_name, "")
            
        self.tree_records.item(item_id, values=current_values)

    def _toggle_column(self, col_name: str, hide: bool):
        if hide:
            self._hidden_columns.add(col_name)
        else:
            self._hidden_columns.discard(col_name)
            # Remove individual cell hidden states for this column to completely clear it
            self._hidden_cells = {k for k in self._hidden_cells if k[1] != col_name}
        
        self.load_records_page()
