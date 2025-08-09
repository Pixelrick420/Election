# ----------------------------
# File: election_app/dialogs.py
# ----------------------------
"""Dialogs used by the UI: Add/Edit Election and Candidate dialog classes."""
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os

class ElectionDialog(simpledialog.Dialog):
    """Modal dialog to create a new election."""
    def body(self, master):
        tk.Label(master, text="Election Name:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        e = tk.Entry(master, textvariable=self.name_var, width=40)
        e.grid(row=0, column=1, pady=5)
        e.focus_set()

        tk.Label(master, text="Admin Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.pw_var = tk.StringVar()
        pw = tk.Entry(master, textvariable=self.pw_var, show='*', width=40)
        pw.grid(row=1, column=1, pady=5)

        return e

    def validate(self):
        name = self.name_var.get().strip()
        pw = self.pw_var.get()
        if not name or not pw:
            messagebox.showerror("Validation", "Please provide name and password.")
            return False
        return True

    def apply(self):
        self.result = (self.name_var.get().strip(), self.pw_var.get())


class CandidateDialog(tk.Toplevel):
    def __init__(self, parent, candidate=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Add / Edit Candidate")
        self.resizable(False, False)
        self.candidate = candidate
        self.symbol_path = candidate['symbol_path'] if candidate else ''

        self._build()
        if candidate:
            self._populate()

    def _build(self):
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky='w', padx=8, pady=6)
        self.name_var = tk.StringVar()
        e = tk.Entry(self, textvariable=self.name_var, width=40)
        e.grid(row=0, column=1, padx=8, pady=6)
        e.focus_set()

        tk.Label(self, text="Symbol (optional):").grid(row=1, column=0, sticky='w', padx=8, pady=6)
        self.symbol_label = tk.Label(self, text=os.path.basename(self.symbol_path) if self.symbol_path else 'No file')
        self.symbol_label.grid(row=1, column=1, sticky='w', padx=8, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text='Browse', command=self._browse).pack(side='left', padx=6)
        tk.Button(btn_frame, text='Clear', command=self._clear).pack(side='left', padx=6)
        tk.Button(btn_frame, text='OK', command=self._ok).pack(side='left', padx=6)
        tk.Button(btn_frame, text='Cancel', command=self._cancel).pack(side='left', padx=6)

    def _populate(self):
        if self.candidate:
            self.name_var.set(self.candidate['name'])

    def _browse(self):
        # Get the symbols directory path relative to the application root
        try:
            symbols_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'symbols')
            initial_dir = symbols_dir if os.path.exists(symbols_dir) else os.getcwd()
        except:
            initial_dir = os.getcwd()
        
        p = filedialog.askopenfilename(
            title='Select image',
            initialdir=initial_dir,
            filetypes=[('Images','*.png *.jpg *.jpeg *.gif *.bmp')]
        )
        if p:
            self.symbol_path = p
            self.symbol_label.config(text=os.path.basename(p))

    def _clear(self):
        self.symbol_path = ''
        self.symbol_label.config(text='No file')

    def _ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror('Error', 'Name is required')
            return
        self.result = {'name': name, 'symbol_path': self.symbol_path}
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()