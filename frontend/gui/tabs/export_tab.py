import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox

class ExportTab(ttk.Frame):
    def __init__(self, master, on_export_request, **kwargs):
        super().__init__(master, **kwargs)
        self.on_export_request = on_export_request
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Export Settings", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky=W, pady=15)

        ttk.Label(self, text="Output Folder Path:").grid(row=1, column=0, sticky=W, pady=5)
        
        try:
            from backend.config import app_config
            default_output = app_config.get_work_dir()
        except Exception:
            default_output = ""
            
        self.var_output_folder = ttk.StringVar(value=default_output)
        ttk.Entry(self, textvariable=self.var_output_folder, width=40).grid(row=1, column=1, sticky=W, pady=5)
        ttk.Button(self, text="Browse", command=lambda: self._browse_folder(self.var_output_folder)).grid(row=1, column=2, padx=5)

        ttk.Label(self, text="Output Filename (without .apkg):").grid(row=2, column=0, sticky=W, pady=5)
        self.var_output_filename = ttk.StringVar()
        ttk.Entry(self, textvariable=self.var_output_filename, width=40).grid(row=2, column=1, sticky=W, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=30)
        ttk.Button(btn_frame, text="Export Deck", bootstyle=SUCCESS, command=self._validate_and_export).pack()

    def _browse_folder(self, string_var):
        path = filedialog.askdirectory()
        if path:
            string_var.set(path)

    def _validate_and_export(self):
        output_folder = self.var_output_folder.get().strip()
        output_filename = self.var_output_filename.get().strip()
        
        if not output_folder:
            messagebox.showerror("Validation Error", "Output Folder Path cannot be empty.")
            return
            
        if not output_filename:
            messagebox.showerror("Validation Error", "Output Filename cannot be empty.")
            return

        self.on_export_request(output_folder, output_filename)
