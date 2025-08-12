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
    root.geometry('1140x650') 

    app = ElectionApp(root)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()


class ElectionApp:
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()
        self.current_election_id = None
        self._loading_elections = False  # Flag to prevent recursive loading

        self._build_ui()
        self._load_elections()

    def _build_ui(self):
        menubar = tk.Menu(self.root, font=('Arial', 11)) 
        file_menu = tk.Menu(menubar, tearoff=0, font=('Arial', 11))  
        file_menu.add_command(label='Export Results', command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.on_close)
        menubar.add_cascade(label='File', menu=file_menu)
        self.root.config(menu=menubar)

        main = tk.Frame(self.root)
        main.pack(fill='both', expand=True)

        left = tk.Frame(main, width=280, bd=1, relief='sunken')  
        left.pack(side='left', fill='y')

        hdr = tk.Frame(left)
        hdr.pack(fill='x', padx=16, pady=8)  
        tk.Label(hdr, text='Elections', font=('Arial', 14, 'bold')).pack(side='left')  
        
        btn_frame = tk.Frame(hdr)
        btn_frame.pack(side='right')
        
        add_btn = tk.Button(btn_frame, text='Add', width=7, height=1, bg='#28a745', fg='white', 
                           font=('Arial', 11, 'bold'), relief='raised', bd=2,  
                           activebackground='#218838', activeforeground='white',
                           command=self.create_election_dialog)
        add_btn.pack(side='left', padx=(0,4))  
        
        del_btn = tk.Button(btn_frame, text='Delete', width=7, height=1, bg='#dc3545', fg='white',
                           font=('Arial', 11, 'bold'), relief='raised', bd=2,  
                           activebackground='#c82333', activeforeground='white',
                           command=self.delete_election_dialog)
        del_btn.pack(side='left')

        self.election_list = tk.Listbox(left, width=43, selectbackground='#007bff', 
                                       selectforeground='white', font=('Arial', 12),  
                                       relief='sunken', bd=2)
        self.election_list.pack(fill='both', expand=True, padx=8, pady=(4,8)) 
        self.election_list.bind('<<ListboxSelect>>', self._on_election_select)

        right = tk.Frame(main, bd=0)
        right.pack(side='right', fill='both', expand=True)

        top_info = tk.Frame(right)
        top_info.pack(fill='x', padx=18, pady=12) 
        self.election_label = tk.Label(top_info, text='No election selected', 
                                      font=('Arial', 12, 'bold'), fg='#343a40')  
        self.election_label.pack(side='left')

        ctrl = tk.Frame(top_info)
        ctrl.pack(side='right')
        
        start_btn = tk.Button(ctrl, text='Start', bg='#28a745', fg='white', 
                             font=('Arial', 12, 'bold'), padx=18, pady=6,  
                             relief='raised', bd=2, activebackground='#218838',
                             command=self.start_voting)
        start_btn.pack(side='left', padx=6)  
        
        view_btn = tk.Button(ctrl, text='View', bg='#17a2b8', fg='white',
                            font=('Arial', 12, 'bold'), padx=18, pady=6,  
                            relief='raised', bd=2, activebackground='#138496',
                            command=self.view_results)
        view_btn.pack(side='left', padx=6) 
        
        clear_btn = tk.Button(ctrl, text='Clear', bg='#ffc107', fg='black',
                             font=('Arial', 12, 'bold'), padx=18, pady=6,  
                             relief='raised', bd=2, activebackground='#e0a800',
                             command=self.clear_results)
        clear_btn.pack(side='left', padx=6) 
        
        export_btn = tk.Button(ctrl, text='Export', bg='#6c757d', fg='white',
                              font=('Arial', 12, 'bold'), padx=18, pady=6, 
                              relief='raised', bd=2, activebackground='#5a6268',
                              command=self.export_results)
        export_btn.pack(side='left', padx=6)  

        cand_frame = tk.LabelFrame(right, text='Candidates', font=('Arial', 14, 'bold'), 
                                  fg='#343a40', relief='groove', bd=2)
        cand_frame.pack(fill='both', expand=True, padx=18, pady=12) 

        tree_frame = tk.Frame(cand_frame)
        tree_frame.pack(fill='both', expand=True, padx=12, pady=12)  

        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 12)) 
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold')) 

        self.tree = ttk.Treeview(tree_frame, columns=('id','name','symbol'), show='headings', selectmode='browse')
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Name')
        self.tree.heading('symbol', text='Symbol')
        self.tree.column('id', width=72, anchor='center') 
        self.tree.column('name', width=360)  
        self.tree.column('symbol', width=180) 
        self.tree.pack(side='left', fill='both', expand=True)

        sb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')

        btns = tk.Frame(right)
        btns.pack(fill='x', padx=18, pady=(0,18)) 
        
        add_cand_btn = tk.Button(btns, text='Add Candidate', bg='#28a745', fg='white',
                                font=('Arial', 12, 'bold'), padx=18, pady=6,
                                relief='raised', bd=2, activebackground='#218838',
                                command=self.add_candidate)
        add_cand_btn.pack(side='left', padx=(0,10))  
        
        edit_cand_btn = tk.Button(btns, text='Edit Candidate', bg='#007bff', fg='white',
                                 font=('Arial', 12, 'bold'), padx=18, pady=6, 
                                 relief='raised', bd=2, activebackground='#0056b3',
                                 command=self.edit_candidate)
        edit_cand_btn.pack(side='left', padx=(0,10)) 
        
        del_cand_btn = tk.Button(btns, text='Delete Candidate', bg='#dc3545', fg='white',
                                font=('Arial', 12, 'bold'), padx=18, pady=6, 
                                relief='raised', bd=2, activebackground='#c82333',
                                command=self.delete_candidate)
        del_cand_btn.pack(side='left')

    def _validate_symbol_uniqueness(self, symbol_path, candidate_id=None):
        """Check if symbol is unique within the current election"""
        if not symbol_path or not self.current_election_id:
            return True
            
        symbol_path = os.path.normpath(symbol_path)
        
        if candidate_id:
            existing = self.db.execute('''
                SELECT id, name FROM Candidates 
                WHERE election_id = ? AND symbol_path = ? AND id != ? AND (is_nota IS NULL OR is_nota = 0)
            ''', (self.current_election_id, symbol_path, candidate_id), fetch=True)
        else:
            existing = self.db.execute('''
                SELECT id, name FROM Candidates 
                WHERE election_id = ? AND symbol_path = ? AND (is_nota IS NULL OR is_nota = 0)
            ''', (self.current_election_id, symbol_path), fetch=True)
        
        if existing:
            candidate_names = [name for _, name in existing]
            messagebox.showerror('Duplicate Symbol', 
                               f'This symbol is already used by: {", ".join(candidate_names)}\n\n'
                               'Each candidate must have a unique symbol.')
            return False
        return True

    def _validate_election_symbols(self):
        """Validate that all candidates have unique symbols and no missing symbols"""
        if not self.current_election_id:
            return False, "No election selected"
            
        candidates = self.db.execute('''
            SELECT id, name, symbol_path FROM Candidates 
            WHERE election_id = ? AND (is_nota IS NULL OR is_nota = 0)
        ''', (self.current_election_id,), fetch=True)
        
        if not candidates:
            return False, "No candidates found"
        
        missing_symbols = []
        symbol_paths = []
        
        for cid, name, symbol_path in candidates:
            if not symbol_path or not os.path.exists(symbol_path):
                missing_symbols.append(name)
            else:
                normalized_path = os.path.normpath(symbol_path)
                symbol_paths.append((normalized_path, name))
        
        if missing_symbols:
            return False, f"Missing symbols for: {', '.join(missing_symbols)}"
        
        seen_symbols = {}
        duplicates = []
        
        for symbol_path, name in symbol_paths:
            if symbol_path in seen_symbols:
                duplicates.append(f"{name} and {seen_symbols[symbol_path]}")
            else:
                seen_symbols[symbol_path] = name
        
        if duplicates:
            return False, f"Duplicate symbols found: {'; '.join(duplicates)}"
        
        return True, "All symbols are valid and unique"

    def _load_elections(self, maintain_selection=True):
        """Load elections list and optionally maintain current selection"""
        if self._loading_elections:  # Prevent recursive calls
            return
            
        self._loading_elections = True
        
        try:
            # Store current selection info before clearing
            current_selection_id = None
            if maintain_selection and hasattr(self, 'current_election_id'):
                current_selection_id = self.current_election_id
            
            # Clear and reload the list
            self.election_list.delete(0, 'end')
            rows = self.db.execute('SELECT id, name FROM Elections ORDER BY created_at DESC', fetch=True)
            self._elections = rows
            
            # Populate the list
            for eid, name in rows:
                self.election_list.insert('end', f"{name} (ID:{eid})")
            
            # Restore selection if requested and election still exists
            if maintain_selection and current_selection_id:
                for idx, (eid, name) in enumerate(self._elections):
                    if eid == current_selection_id:
                        self.election_list.selection_clear(0, 'end')
                        self.election_list.selection_set(idx)
                        self.election_list.activate(idx)
                        self.election_list.see(idx)
                        break
                        
        finally:
            self._loading_elections = False

    def create_election_dialog(self):
        d = ElectionDialog(self.root)
        if getattr(d, 'result', None):
            name, pw = d.result
            try:
                from .security import SecurityManager
                h = SecurityManager.hash_password(pw)
                eid = self.db.execute('INSERT INTO Elections (name, admin_password_hash) VALUES (?, ?)', (name, h))
                self._load_elections(maintain_selection=False)
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
        
        pw = simpledialog.askstring('Admin Password', f'Enter admin password to delete "{name}":', show='*')
        if pw is None:
            return
            
        stored = self.db.execute('SELECT admin_password_hash FROM Elections WHERE id = ?', (eid,), fetch=True)
        if not stored or not SecurityManager.verify_password(pw, stored[0][0]):
            messagebox.showerror('Invalid', 'Incorrect password')
            return
            
        if not messagebox.askyesno('Confirm Deletion', 
                                  f'Are you sure you want to delete election "{name}"?\n\n'
                                  'This will permanently delete all candidates and votes!'):
            return
        
        self.db.execute('DELETE FROM Elections WHERE id = ?', (eid,))
        
        # Clear current selection if we deleted the current election
        if hasattr(self, 'current_election_id') and self.current_election_id == eid:
            self.current_election_id = None
            self.election_label.config(text='No election selected')
            self._refresh_candidates()
            
        self._load_elections(maintain_selection=False)
        messagebox.showinfo('Deleted', f'Election "{name}" has been deleted.')

    def _select_election_by_id(self, eid):
        """Select an election by ID and handle the selection properly"""
        self._load_elections(maintain_selection=False)
        
        # Force UI update
        self.root.update()
        
        for idx, (id_, name) in enumerate(self._elections):
            if id_ == eid:
                self.election_list.selection_clear(0, 'end')
                self.election_list.selection_set(idx)
                self.election_list.activate(idx)
                self.election_list.see(idx)
                
                # Force UI update after selection
                self.root.update()
                
                self._set_current_election(id_, name)
                return True
        return False

    def _on_election_select(self, event=None):
        """Handle election selection from the listbox"""
        if self._loading_elections:  # Ignore selection events during loading
            return
            
        sel = self.election_list.curselection()
        if not sel:
            # No selection - clear current election
            self.current_election_id = None
            self.election_label.config(text='No election selected')
            self._refresh_candidates()
            return
            
        idx = sel[0]
        if idx >= len(self._elections):  # Safety check
            return
            
        eid, name = self._elections[idx]
        
        # If this is already the current election, don't do anything
        if hasattr(self, 'current_election_id') and self.current_election_id == eid:
            return
        
        # Store the current state in case we need to restore
        prev_election_id = getattr(self, 'current_election_id', None)
        prev_election_name = None
        if prev_election_id:
            for prev_id, prev_name in self._elections:
                if prev_id == prev_election_id:
                    prev_election_name = prev_name
                    break
        
        # Prompt for password
        pw = simpledialog.askstring('Admin Password', f'Enter admin password for "{name}":', show='*')
        if pw is None:
            # User cancelled - restore previous selection
            if prev_election_id and prev_election_name:
                # Force restore previous election
                self.election_list.selection_clear(0, 'end')
                self._loading_elections = True  # Prevent recursive calls
                try:
                    for restore_idx, (restore_id, _) in enumerate(self._elections):
                        if restore_id == prev_election_id:
                            self.election_list.selection_set(restore_idx)
                            self.election_list.activate(restore_idx)
                            break
                    self.current_election_id = prev_election_id
                    self.election_label.config(text=f"Election: {prev_election_name}")
                    self._refresh_candidates()
                finally:
                    self._loading_elections = False
            else:
                self.election_list.selection_clear(0, 'end')
                self.current_election_id = None
                self.election_label.config(text='No election selected')
                self._refresh_candidates()
            self.root.update()
            return
            
        # Verify password
        stored = self.db.execute('SELECT admin_password_hash FROM Elections WHERE id = ?', (eid,), fetch=True)
        if not stored or not SecurityManager.verify_password(pw, stored[0][0]):
            messagebox.showerror('Invalid', 'Incorrect password')
            # Restore previous selection
            if prev_election_id and prev_election_name:
                # Force restore previous election
                self.election_list.selection_clear(0, 'end')
                self._loading_elections = True  # Prevent recursive calls
                try:
                    for restore_idx, (restore_id, _) in enumerate(self._elections):
                        if restore_id == prev_election_id:
                            self.election_list.selection_set(restore_idx)
                            self.election_list.activate(restore_idx)
                            break
                    self.current_election_id = prev_election_id
                    self.election_label.config(text=f"Election: {prev_election_name}")
                    self._refresh_candidates()
                finally:
                    self._loading_elections = False
            else:
                self.election_list.selection_clear(0, 'end')
                self.current_election_id = None
                self.election_label.config(text='No election selected')
                self._refresh_candidates()
            self.root.update()
            return
            
        # Password is correct - set the current election
        self._set_current_election(eid, name)

    def _set_current_election(self, eid, name):
        """Set the current election and update the UI"""
        # Clear everything first
        self.current_election_id = None
        self.election_label.config(text='Loading...')
        
        # Clear candidates immediately
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Force UI update
        self.root.update()
        
        # Now set the new election
        self.current_election_id = eid
        self.election_label.config(text=f"Election: {name}")
        
        # Force another UI update
        self.root.update()
        
        # Refresh candidates with the new election
        self._refresh_candidates()
        
        # Final UI update to ensure everything is displayed
        self.root.update()

    def _refresh_candidates(self):
        """Refresh the candidates list for the current election"""
        # Force clear all existing items with multiple approaches for reliability
        try:
            # Method 1: Bulk delete (fastest)
            items = self.tree.get_children()
            if items:
                self.tree.delete(*items)
        except:
            # Method 2: Individual delete (fallback)
            for i in self.tree.get_children():
                try:
                    self.tree.delete(i)
                except:
                    pass
        
        # Force multiple UI updates to ensure clearing is processed on all systems
        self.tree.update_idletasks()
        self.root.update_idletasks()
        self.root.update()
            
        # If no election is selected, just clear and return
        if not self.current_election_id:
            # Additional UI updates to ensure empty state is displayed
            self.tree.update_idletasks()
            self.root.update_idletasks()
            self.root.update()
            return
            
        # Get candidates for the current election only
        try:
            rows = self.db.execute('''
                SELECT id, name, symbol_path FROM Candidates 
                WHERE election_id = ? AND (is_nota IS NULL OR is_nota = 0)
                ORDER BY id
            ''', (self.current_election_id,), fetch=True)
        except Exception as e:
            print(f"Database error: {e}")
            rows = []
        
        # Add candidates to the tree
        for cid, name, symbol_path in rows:
            try:
                if not symbol_path:
                    symbol_display = 'No Symbol'
                elif not os.path.exists(symbol_path):
                    symbol_display = f'{os.path.basename(symbol_path)} (Missing)'
                else:
                    symbol_display = os.path.basename(symbol_path)
                self.tree.insert('', 'end', values=(cid, name, symbol_display))
            except Exception as e:
                print(f"Tree insert error: {e}")
        
        # Force multiple UI updates to ensure changes are visible on all systems
        self.tree.update_idletasks()
        self.root.update_idletasks()
        self.root.update()
    def add_candidate(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        d = CandidateDialog(self.root)
        self.root.wait_window(d)
        if getattr(d, 'result', None):
            r = d.result
            
            if not r['symbol_path'] or not r['symbol_path'].strip():
                messagebox.showerror('Missing Symbol', 'Each candidate must have a symbol assigned.')
                return
            
            if not os.path.exists(r['symbol_path']):
                messagebox.showerror('Invalid Symbol', f'Symbol file does not exist:\n{r["symbol_path"]}')
                return
            
            if not self._validate_symbol_uniqueness(r['symbol_path']):
                return
            
            self.db.execute('INSERT INTO Candidates (election_id, name, symbol_path) VALUES (?, ?, ?)',
                            (self.current_election_id, r['name'], r['symbol_path']))
            self._refresh_candidates()
            messagebox.showinfo('Success', f'Candidate "{r["name"]}" added successfully.')

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
            
            if not r['symbol_path'] or not r['symbol_path'].strip():
                messagebox.showerror('Missing Symbol', 'Each candidate must have a symbol assigned.')
                return
            
            if not os.path.exists(r['symbol_path']):
                messagebox.showerror('Invalid Symbol', f'Symbol file does not exist:\n{r["symbol_path"]}')
                return
            
            if not self._validate_symbol_uniqueness(r['symbol_path'], cid):
                return
            
            self.db.execute('UPDATE Candidates SET name = ?, symbol_path = ? WHERE id = ?',
                            (r['name'], r['symbol_path'], cid))
            self._refresh_candidates()
            messagebox.showinfo('Success', f'Candidate "{r["name"]}" updated successfully.')

    def delete_candidate(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror('Error', 'Select a candidate')
            return
        if not messagebox.askyesno('Confirm', 'Delete candidate and all associated votes?'):
            return
        item = self.tree.item(sel[0])
        cid = item['values'][0]
        candidate_name = item['values'][1]
        
        self.db.execute('DELETE FROM Votes WHERE candidate_id = ?', (cid,))
        self.db.execute('DELETE FROM Candidates WHERE id = ?', (cid,))
        self._refresh_candidates()
        messagebox.showinfo('Deleted', f'Candidate "{candidate_name}" has been deleted.')

    def start_voting(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        count = self.db.execute('SELECT COUNT(*) FROM Candidates WHERE election_id = ? AND (is_nota IS NULL OR is_nota = 0)', (self.current_election_id,), fetch=True)[0][0]
        if count < 1:  
            messagebox.showerror('Error', 'Need at least 1 candidate')
            return
        
        is_valid, message = self._validate_election_symbols()
        if not is_valid:
            messagebox.showerror('Symbol Validation Error', 
                               f'Cannot start voting due to symbol issues:\n\n{message}\n\n'
                               'Please fix these issues before starting the election.')
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
        w.geometry('840x600')  
        w.configure(bg='#f8f9fa')
        
        title_frame = tk.Frame(w, bg='#f8f9fa')
        title_frame.pack(fill='x', pady=18)  
        tk.Label(title_frame, text=f"Results for Election ID: {self.current_election_id}", 
                font=('Arial', 19, 'bold'), bg='#f8f9fa', fg='#343a40').pack()  

        tree_frame = tk.Frame(w, bg='#f8f9fa')
        tree_frame.pack(fill='both', expand=True, padx=24, pady=(0,24))  
        
        results_style = ttk.Style()
        results_style.configure("Results.Treeview", font=('Arial', 12)) 
        results_style.configure("Results.Treeview.Heading", font=('Arial', 13, 'bold'))  
        
        tree = ttk.Treeview(tree_frame, columns=('Votes','Percent'), show='tree headings', style="Results.Treeview")
        tree.heading('#0', text='Candidate')
        tree.heading('Votes', text='Votes')
        tree.heading('Percent', text='Percentage')
        tree.column('#0', width=420)  
        tree.column('Votes', width=144, anchor='center') 
        tree.column('Percent', width=144, anchor='center')  
        tree.pack(fill='both', expand=True)

        for name, votes in rows:
            percent = (votes/total*100) if total else 0
            tree.insert('', 'end', text=name, values=(votes, f"{percent:.2f}%"))

        close_btn = tk.Button(w, text='Close', bg='#6c757d', fg='white',
                             font=('Arial', 13, 'bold'), padx=24, pady=10,  
                             relief='raised', bd=2, activebackground='#5a6268',
                             command=w.destroy)
        close_btn.pack(pady=18)  

    def clear_results(self):
        if not self.current_election_id:
            messagebox.showerror('Error', 'Select an election first')
            return
        
        if not messagebox.askyesno('Confirm Clear', 
                                  'Are you sure you want to clear all votes for this election?\n\n'
                                  'This action cannot be undone!'):
            return
        
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