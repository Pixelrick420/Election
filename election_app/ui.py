"""Main UI module. Creates a left panel with elections and Add/Delete buttons, and a right panel for candidate management.
Provides a cleaner flow for creating/loading elections and starting voting."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from .db import DatabaseManager
from .security import SecurityManager
from .exporter import ResultsExporter
from .dialogs import CandidateDialog, ElectionDialog
from .voting import VotingInterface

APP_TITLE = "Election Management System"


def run_app():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry('1300x650')  # Back to original size, optimized padding instead

    app = ElectionApp(root)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()


class ElectionApp:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()
        self.current_election_id = None

        self._build_ui()
        self._load_elections()

    def _build_ui(self):
        # Top menu
        menubar = tk.Menu(self.root, font=('Arial', 11))  # Increased from default
        file_menu = tk.Menu(menubar, tearoff=0, font=('Arial', 11))  # Increased from default
        file_menu.add_command(label='Export Results', command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.on_close)
        menubar.add_cascade(label='File', menu=file_menu)
        self.root.config(menu=menubar)

        main = tk.Frame(self.root)
        main.pack(fill='both', expand=True)

        # Left panel: Elections list with Add/Delete buttons
        left = tk.Frame(main, width=320, bd=1, relief='sunken')  # Reduced from 336
        left.pack(side='left', fill='y')

        hdr = tk.Frame(left)
        hdr.pack(fill='x', padx=8, pady=8)  # Reduced from 12
        tk.Label(hdr, text='Elections', font=('Arial', 17, 'bold')).pack(side='left')  # Keep large font
        
        btn_frame = tk.Frame(hdr)
        btn_frame.pack(side='right')
        
        # Green Add button
        add_btn = tk.Button(btn_frame, text='Add', width=7, height=1, bg='#28a745', fg='white', 
                           font=('Arial', 11, 'bold'), relief='raised', bd=2,  # Keep font size
                           activebackground='#218838', activeforeground='white',
                           command=self.create_election_dialog)
        add_btn.pack(side='left', padx=(0,4))  # Reduced from 6
        
        # Red Delete button  
        del_btn = tk.Button(btn_frame, text='Delete', width=7, height=1, bg='#dc3545', fg='white',
                           font=('Arial', 11, 'bold'), relief='raised', bd=2,  # Keep font size
                           activebackground='#c82333', activeforeground='white',
                           command=self.delete_election_dialog)
        del_btn.pack(side='left')

        self.election_list = tk.Listbox(left, width=43, selectbackground='#007bff',  # Reduced from 45
                                       selectforeground='white', font=('Arial', 12),  # Keep font size
                                       relief='sunken', bd=2)
        self.election_list.pack(fill='both', expand=True, padx=8, pady=(4,8))  # Reduced padding
        self.election_list.bind('<<ListboxSelect>>', self._on_election_select)

        # Right panel: Candidate management and controls
        right = tk.Frame(main, bd=0)
        right.pack(side='right', fill='both', expand=True)

        top_info = tk.Frame(right)
        top_info.pack(fill='x', padx=18, pady=12)  # Increased padding
        self.election_label = tk.Label(top_info, text='No election selected', 
                                      font=('Arial', 19, 'bold'), fg='#343a40')  # Increased from 16
        self.election_label.pack(side='left')

        ctrl = tk.Frame(top_info)
        ctrl.pack(side='right')
        
        # Styled control buttons
        start_btn = tk.Button(ctrl, text='Start Voting', bg='#28a745', fg='white', 
                             font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                             relief='raised', bd=2, activebackground='#218838',
                             command=self.start_voting)
        start_btn.pack(side='left', padx=6)  # Increased padding
        
        view_btn = tk.Button(ctrl, text='View Results', bg='#17a2b8', fg='white',
                            font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                            relief='raised', bd=2, activebackground='#138496',
                            command=self.view_results)
        view_btn.pack(side='left', padx=6)  # Increased padding
        
        clear_btn = tk.Button(ctrl, text='Clear Results', bg='#ffc107', fg='black',
                             font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                             relief='raised', bd=2, activebackground='#e0a800',
                             command=self.clear_results)
        clear_btn.pack(side='left', padx=6)  # Increased padding
        
        export_btn = tk.Button(ctrl, text='Export', bg='#6c757d', fg='white',
                              font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                              relief='raised', bd=2, activebackground='#5a6268',
                              command=self.export_results)
        export_btn.pack(side='left', padx=6)  # Increased padding

        # Candidates section with improved styling
        cand_frame = tk.LabelFrame(right, text='Candidates', font=('Arial', 14, 'bold'),  # Increased from 12
                                  fg='#343a40', relief='groove', bd=2)
        cand_frame.pack(fill='both', expand=True, padx=18, pady=12)  # Increased padding

        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(cand_frame)
        tree_frame.pack(fill='both', expand=True, padx=12, pady=12)  # Increased padding

        # Configure ttk style for larger fonts
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 12))  # Increased from default
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))  # Increased from default

        self.tree = ttk.Treeview(tree_frame, columns=('id','name','symbol'), show='headings', selectmode='browse')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Name')
        self.tree.heading('symbol', text='Symbol File')
        self.tree.column('id', width=72, anchor='center')  # Increased from 60
        self.tree.column('name', width=360)  # Increased from 300
        self.tree.column('symbol', width=180)  # Increased from 150
        self.tree.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        # Candidate management buttons with improved styling
        btns = tk.Frame(right)
        btns.pack(fill='x', padx=18, pady=(0,18))  # Increased padding
        
        add_cand_btn = tk.Button(btns, text='Add Candidate', bg='#28a745', fg='white',
                                font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                                relief='raised', bd=2, activebackground='#218838',
                                command=self.add_candidate)
        add_cand_btn.pack(side='left', padx=(0,10))  # Increased padding
        
        edit_cand_btn = tk.Button(btns, text='Edit Candidate', bg='#007bff', fg='white',
                                 font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                                 relief='raised', bd=2, activebackground='#0056b3',
                                 command=self.edit_candidate)
        edit_cand_btn.pack(side='left', padx=(0,10))  # Increased padding
        
        del_cand_btn = tk.Button(btns, text='Delete Candidate', bg='#dc3545', fg='white',
                                font=('Arial', 12, 'bold'), padx=18, pady=6,  # Increased from 10, 15, 5
                                relief='raised', bd=2, activebackground='#c82333',
                                command=self.delete_candidate)
        del_cand_btn.pack(side='left')

    def _load_elections(self):
        self.election_list.delete(0, 'end')
        rows = self.db.execute('SELECT id, name FROM Elections ORDER BY created_at DESC', fetch=True)
        self._elections = rows
        for eid, name in rows:
            self.election_list.insert('end', f"{name} (ID:{eid})")
        
        # Highlight currently selected election
        if hasattr(self, 'current_election_id') and self.current_election_id:
            for idx, (id_, name) in enumerate(self._elections):
                if id_ == self.current_election_id:
                    self.election_list.selection_set(idx)
                    self.election_list.activate(idx)
                    break

    def create_election_dialog(self):
        d = ElectionDialog(self.root)
        if getattr(d, 'result', None):
            name, pw = d.result
            # create election
            try:
                from .security import SecurityManager
                h = SecurityManager.hash_password(pw)
                eid = self.db.execute('INSERT INTO Elections (name, admin_password_hash) VALUES (?, ?)', (name, h))
                self._load_elections()
                # auto-select the newly created election
                self._select_election_by_id(eid)
                messagebox.showinfo('Created', f"Election '{name}' created.")
            except Exception as e:
                messagebox.showerror('Error', str(e))

    def delete_election_dialog(self):
        sel = self.election_list.curselection()
        if not sel:
            messagebox.showerror('Error', 'Select an election to delete')
            return
        
        idx = sel[0]
        eid, name = self._elections[idx]
        
        # Always ask for password regardless of selection
        pw = simpledialog.askstring('Admin Password', f'Enter admin password to delete "{name}":', show='*')
        if pw is None:
            return
            
        stored = self.db.execute('SELECT admin_password_hash FROM Elections WHERE id = ?', (eid,), fetch=True)
        if not stored or not SecurityManager.verify_password(pw, stored[0][0]):
            messagebox.showerror('Invalid', 'Incorrect password')
            return
            
        # Confirm deletion
        if not messagebox.askyesno('Confirm Deletion', 
                                  f'Are you sure you want to delete election "{name}"?\n\n'
                                  'This will permanently delete all candidates and votes!'):
            return
        
        # Delete election (cascade will handle candidates and votes)
        self.db.execute('DELETE FROM Elections WHERE id = ?', (eid,))
        
        # Clear current selection if deleted election was selected
        if hasattr(self, 'current_election_id') and self.current_election_id == eid:
            self.current_election_id = None
            self.election_label.config(text='No election selected')
            self._refresh_candidates()
            
        self._load_elections()
        messagebox.showinfo('Deleted', f'Election "{name}" has been deleted.')

    def _select_election_by_id(self, eid):
        # refresh list and select the appropriate index
        self._load_elections()
        for idx, (id_, name) in enumerate(self._elections):
            if id_ == eid:
                self.election_list.selection_set(idx)
                self.election_list.activate(idx)
                self.election_list.see(idx)
                self._set_current_election(id_, name)
                return

    def _on_election_select(self, event=None):
        sel = self.election_list.curselection()
        if not sel:
            return
        idx = sel[0]
        eid, name = self._elections[idx]
        
        # If clicking on already selected election, don't prompt for password
        if hasattr(self, 'current_election_id') and self.current_election_id == eid:
            return
        
        # prompt for admin password when loading existing election
        pw = simpledialog.askstring('Admin Password', 'Enter admin password:', show='*')
        if pw is None:
            # undo selection and restore previous selection
            self._load_elections()  # This will restore the previous selection highlighting
            return
        stored = self.db.execute('SELECT admin_password_hash FROM Elections WHERE id = ?', (eid,), fetch=True)
        if not stored or not SecurityManager.verify_password(pw, stored[0][0]):
            messagebox.showerror('Invalid', 'Incorrect password')
            self._load_elections()  # This will restore the previous selection highlighting
            return
        self._set_current_election(eid, name)

    def _set_current_election(self, eid, name):
        self.current_election_id = eid
        self.election_label.config(text=f"Election: {name}")
        self._refresh_candidates()
        self._load_elections()  # Refresh to update highlighting

    def _refresh_candidates(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if not self.current_election_id:
            return
        rows = self.db.execute('SELECT id, name, symbol_path FROM Candidates WHERE election_id = ? AND (is_nota IS NULL OR is_nota = 0)', (self.current_election_id,), fetch=True)
        for cid, name, symbol_path in rows:
            # Extract just the filename from the full path
            symbol_filename = os.path.basename(symbol_path) if symbol_path else 'No Symbol'
            self.tree.insert('', 'end', values=(cid, name, symbol_filename))

    def add_candidate(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        d = CandidateDialog(self.root)
        self.root.wait_window(d)
        if getattr(d, 'result', None):
            r = d.result
            self.db.execute('INSERT INTO Candidates (election_id, name, symbol_path) VALUES (?, ?, ?)',
                            (self.current_election_id, r['name'], r['symbol_path']))
            self._refresh_candidates()

    def edit_candidate(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror('Error', 'Select a candidate')
            return
        item = self.tree.item(sel[0])
        cid = item['values'][0]
        row = self.db.execute('SELECT name, symbol_path FROM Candidates WHERE id = ?', (cid,), fetch=True)[0]
        cand = {'name': row[0], 'symbol_path': row[1] or ''}
        d = CandidateDialog(self.root, candidate=cand)
        self.root.wait_window(d)
        if getattr(d, 'result', None):
            r = d.result
            self.db.execute('UPDATE Candidates SET name = ?, symbol_path = ? WHERE id = ?',
                            (r['name'], r['symbol_path'], cid))
            self._refresh_candidates()

    def delete_candidate(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror('Error', 'Select a candidate')
            return
        if not messagebox.askyesno('Confirm', 'Delete candidate and all associated votes?'):
            return
        item = self.tree.item(sel[0])
        cid = item['values'][0]
        self.db.execute('DELETE FROM Votes WHERE candidate_id = ?', (cid,))
        self.db.execute('DELETE FROM Candidates WHERE id = ?', (cid,))
        self._refresh_candidates()

    def start_voting(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        count = self.db.execute('SELECT COUNT(*) FROM Candidates WHERE election_id = ?', (self.current_election_id,), fetch=True)[0][0]
        if count < 1:  # Changed from 2 to 1 since NOTA will be added automatically
            messagebox.showerror('Error', 'Need at least 1 candidate')
            return
        admin_hash = self.db.execute('SELECT admin_password_hash FROM Elections WHERE id = ?', (self.current_election_id,), fetch=True)[0][0]
        VotingInterface(self.root, self.current_election_id, admin_hash, self.db)

    def view_results(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        rows = self.db.execute('''
            SELECT c.name, COUNT(v.id) as votes
            FROM Candidates c
            LEFT JOIN Votes v ON c.id = v.candidate_id
            WHERE c.election_id = ?
            GROUP BY c.id, c.name
            ORDER BY votes DESC
        ''', (self.current_election_id,), fetch=True)
        total = sum(r[1] for r in rows)

        w = tk.Toplevel(self.root)
        w.title('Results')
        w.geometry('840x600')  # Increased from 700x500
        w.configure(bg='#f8f9fa')
        
        # Title with better styling
        title_frame = tk.Frame(w, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=18)  # Increased padding
        tk.Label(title_frame, text=f"Results for Election ID: {self.current_election_id}", 
                font=('Arial', 19, 'bold'), bg='#f8f9fa', fg='#343a40').pack()  # Increased from 16

        # Results tree with better styling
        tree_frame = tk.Frame(w, bg='#f8f9fa')
        tree_frame.pack(fill='both', expand=True, padx=24, pady=(0,24))  # Increased padding
        
        # Configure style for results tree
        results_style = ttk.Style()
        results_style.configure("Results.Treeview", font=('Arial', 12))  # Increased font
        results_style.configure("Results.Treeview.Heading", font=('Arial', 13, 'bold'))  # Increased font
        
        tree = ttk.Treeview(tree_frame, columns=('Votes','Percent'), show='tree headings', style="Results.Treeview")
        tree.heading('#0', text='Candidate')
        tree.heading('Votes', text='Votes')
        tree.heading('Percent', text='Percentage')
        tree.column('#0', width=420)  # Increased from 350
        tree.column('Votes', width=144, anchor='center')  # Increased from 120
        tree.column('Percent', width=144, anchor='center')  # Increased from 120
        tree.pack(fill='both', expand=True)

        for name, votes in rows:
            percent = (votes/total*100) if total else 0
            tree.insert('', 'end', text=name, values=(votes, f"{percent:.2f}%"))

        # Close button with styling
        close_btn = tk.Button(w, text='Close', bg='#6c757d', fg='white',
                             font=('Arial', 13, 'bold'), padx=24, pady=10,  # Increased from 11, 20, 8
                             relief='raised', bd=2, activebackground='#5a6268',
                             command=w.destroy)
        close_btn.pack(pady=18)  # Increased padding

    def clear_results(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        
        if not messagebox.askyesno('Confirm Clear', 
                                  'Are you sure you want to clear all votes for this election?\n\n'
                                  'This action cannot be undone!'):
            return
        
        # Delete all votes for this election
        self.db.execute('DELETE FROM Votes WHERE election_id = ?', (self.current_election_id,))
        messagebox.showinfo('Cleared', 'All votes have been cleared for this election.')

    def export_results(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        out = filedialog.askdirectory(title='Select output directory')
        if not out:
            return
        exporter = ResultsExporter(self.db)
        try:
            j, c, p = exporter.export_results(self.current_election_id, out)
            msg = f'Exported:\n• {os.path.basename(j)}\n• {os.path.basename(c)}'
            if p:
                msg += f"\n• {os.path.basename(p)}"
            messagebox.showinfo('Exported', msg)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def on_close(self):
        if messagebox.askokcancel('Quit', 'Exit application?'):
            self.root.destroy()