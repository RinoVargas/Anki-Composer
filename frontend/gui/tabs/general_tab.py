import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import os
from frontend.gui.template_registry import get_template_names
from frontend.gui.components.sheet_selector import SheetSelector

class GeneralTab(ttk.Frame):
    def __init__(self, master, on_next_step, **kwargs):
        super().__init__(master, **kwargs)
        self.on_next_step = on_next_step
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Deck Name:").grid(row=0, column=0, sticky=W, pady=5)
        self.var_deck_name = ttk.StringVar()
        ttk.Entry(self, textvariable=self.var_deck_name, width=40).grid(row=0, column=1, sticky=W, pady=5)

        ttk.Label(self, text="Input Type:").grid(row=1, column=0, sticky=W, pady=5)
        self.var_input_type = ttk.StringVar(value="xlsx")
        cb_type = ttk.Combobox(self, textvariable=self.var_input_type, values=["xlsx", "csv", "gsheet"], state="readonly", width=38)
        cb_type.grid(row=1, column=1, sticky=W, pady=5)
        cb_type.bind("<<ComboboxSelected>>", self._on_input_type_change)

        ttk.Label(self, text="Input File Path / URL:").grid(row=2, column=0, sticky=W, pady=5)
        self.var_input_file = ttk.StringVar()
        self.var_input_file.trace_add('write', self._on_input_file_change)
        ttk.Entry(self, textvariable=self.var_input_file, width=40).grid(row=2, column=1, sticky=W, pady=5)
        
        self.btn_browse_input = ttk.Button(self, text="Browse", command=lambda: self._browse_file(self.var_input_file))
        self.btn_browse_input.grid(row=2, column=2, padx=5)

        # Sheets Selector Frame
        self.sheet_selector = SheetSelector(self)
        
        ttk.Label(self, text="Media Folder Path:").grid(row=4, column=0, sticky=W, pady=5)
        self.var_media_folder = ttk.StringVar()
        ttk.Entry(self, textvariable=self.var_media_folder, width=40).grid(row=4, column=1, sticky=W, pady=5)
        ttk.Button(self, text="Browse", command=lambda: self._browse_folder(self.var_media_folder)).grid(row=4, column=2, padx=5)

        self.var_disable_audio = ttk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Disable Audio Generation", variable=self.var_disable_audio).grid(row=5, column=0, columnspan=2, sticky=W, pady=5)

        ttk.Label(self, text="Output Folder Path:").grid(row=6, column=0, sticky=W, pady=5)
        self.var_output_folder = ttk.StringVar()
        ttk.Entry(self, textvariable=self.var_output_folder, width=40).grid(row=6, column=1, sticky=W, pady=5)
        ttk.Button(self, text="Browse", command=lambda: self._browse_folder(self.var_output_folder)).grid(row=6, column=2, padx=5)

        ttk.Label(self, text="Output Filename (without .apkg):").grid(row=7, column=0, sticky=W, pady=5)
        self.var_output_filename = ttk.StringVar()
        ttk.Entry(self, textvariable=self.var_output_filename, width=40).grid(row=7, column=1, sticky=W, pady=5)

        ttk.Label(self, text="Template:").grid(row=8, column=0, sticky=W, pady=5)
        self.var_template = ttk.StringVar()
        templates_available = get_template_names()
        cb_template = ttk.Combobox(self, textvariable=self.var_template, values=templates_available, state="readonly", width=38)
        cb_template.grid(row=8, column=1, sticky=W, pady=5)
        if templates_available:
            cb_template.current(0)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=9, column=0, columnspan=3, pady=20)
        ttk.Button(btn_frame, text="Next: Map Fields ➔", bootstyle=PRIMARY, command=self._validate_and_next).pack()

    def _on_input_type_change(self, event=None):
        input_type = self.var_input_type.get()
        
        self.var_input_file.set("")
        self.sheet_selector.clear()
        self.sheet_selector.grid_remove()
        
        if input_type == "gsheet":
            self.btn_browse_input.configure(state="disabled")
        else:
            self.btn_browse_input.configure(state="normal")

    def _on_input_file_change(self, *args):
        input_type = self.var_input_type.get()
        if input_type == "csv":
            self.sheet_selector.grid_remove()
            return
            
        file_path = self.var_input_file.get().strip()
        self.sheet_selector.set_context(input_type, file_path)
        
        if file_path:
            self.sheet_selector.grid(row=3, column=0, columnspan=3, sticky=EW, pady=5)
        else:
            self.sheet_selector.grid_remove()
            self.sheet_selector.clear()

    def _browse_file(self, string_var):
        input_type = self.var_input_type.get()
        filetypes = [("All files", "*.*")]
        
        if input_type == "xlsx":
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
        elif input_type == "csv":
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            string_var.set(path)
            if input_type == "xlsx":
                self.sheet_selector.load_sheets(input_type, path)

    def _browse_folder(self, string_var):
        path = filedialog.askdirectory()
        if path:
            string_var.set(path)

    def _validate_and_next(self):
        if not self.var_deck_name.get().strip():
            messagebox.showerror("Validation Error", "Deck Name cannot be empty.")
            return
        
        input_path = self.var_input_file.get().strip()
        if not input_path:
            messagebox.showerror("Validation Error", "Input File Path cannot be empty.")
            return
        
        if not (input_path.startswith("http://") or input_path.startswith("https://")):
            if not os.path.isfile(input_path):
                messagebox.showerror("Validation Error", f"Input file does not exist locally:\n{input_path}")
                return
                
        if not self.var_output_folder.get().strip():
            messagebox.showerror("Validation Error", "Output Folder Path cannot be empty.")
            return
            
        if not self.var_output_filename.get().strip():
            messagebox.showerror("Validation Error", "Output Filename cannot be empty.")
            return

        if not self.var_template.get():
            messagebox.showerror("Validation Error", "Please select a Template.")
            return
            
        self.on_next_step(self.var_template.get())

    def get_config(self) -> dict:
        return {
            "deck_name": self.var_deck_name.get().strip(),
            "input_type": self.var_input_type.get(),
            "input_file_path": self.var_input_file.get().strip(),
            "media_folder_path": self.var_media_folder.get().strip(),
            "disable_audio_generation": self.var_disable_audio.get(),
            "output_folder_path": self.var_output_folder.get().strip(),
            "output_filename": self.var_output_filename.get().strip(),
            "template_name": self.var_template.get(),
            "sheets_list": self.sheet_selector.get_selected_sheets() if self.var_input_type.get() != "csv" else []
        }
