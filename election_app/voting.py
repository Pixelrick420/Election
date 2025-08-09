"""Voting interface module. Full-screen voting window with button-based selection."""
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import subprocess
import sys
import threading
import time
import math
from PIL import Image, ImageTk
from .security import SecurityManager
from .exporter import ResultsExporter

# UI Configuration Constants
TITLE_TO_TABLE_SPACING = 0  # Space between title and table
TITLE_PADDING = 5  # Padding around the title


def play_beep_sound(frequency=800, duration=0.3):
    """Play a beep sound optimized for Ubuntu 22.04"""
    try:
        import subprocess
        import tempfile
        import wave
        import struct
        import math
        
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            with wave.open(temp_file.name, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                
                for i in range(frames):
                    value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
                    wav_file.writeframes(struct.pack('<h', value))
            
            subprocess.run(['aplay', temp_file.name], 
                          check=False, capture_output=True, timeout=3)
            
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except Exception:
        try:
            subprocess.run(['pactl', 'play-sample', 'bell'], 
                          check=False, capture_output=True, timeout=1)
        except Exception:
            try:
                sys.stdout.write('\a')
                sys.stdout.flush()
            except Exception:
                pass


def play_double_beep():
    """Play double beep for deletion confirmation"""
    def beep_thread():
        play_beep_sound(600, 0.2)
        time.sleep(0.1)
        play_beep_sound(600, 0.2)
    
    threading.Thread(target=beep_thread, daemon=True).start()


class VotingInterface:
    """Full-screen voting window with button-based candidate selection."""
    def __init__(self, parent, election_id, admin_hash, db):
        self.parent = parent
        self.election_id = election_id
        self.admin_hash = admin_hash
        self.db = db
        self.selected_candidate = None
        self.candidates = []
        self.candidate_buttons = []
        self.has_voted_current_ballot = False
        self.awaiting_next_ballot = False

        self.win = tk.Toplevel(parent)
        self.win.title('Voting')
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-topmost', True)
        self.win.configure(bg='white')
        self.win.protocol('WM_DELETE_WINDOW', lambda: None)
        self.win.focus_set()
        self.win.grab_set()

        self.win.bind('<Return>', self._cast_vote)
        self.win.bind('<space>', self._next_ballot)
        self.win.bind('<Tab>', self._delete_last_vote)
        self.win.bind('<Key>', self._on_key)
        self.win.bind('<Escape>', lambda e: 'break')
        self.win.bind('<Alt-Tab>', lambda e: 'break')
        self.win.bind('<Control-Alt-t>', lambda e: 'break')
        self._disable_system_keys()
        
        self.win.protocol("WM_DELETE_WINDOW", self._on_closing)

        self._build()

    def _disable_system_keys(self):
        """Disable system keys using xmodmap on Linux"""
        try:
            # Disable Super (Windows) keys
            subprocess.run(['xmodmap', '-e', 'clear mod4'], check=False, capture_output=True)
            subprocess.run(['xmodmap', '-e', 'keycode 133='], check=False, capture_output=True)  # Left Super
            subprocess.run(['xmodmap', '-e', 'keycode 134='], check=False, capture_output=True)  # Right Super
        except Exception:
            pass
    
    def _restore_system_keys(self):
        """Restore system keys"""
        try:
            # Restore Super keys
            subprocess.run(['xmodmap', '-e', 'keycode 133=Super_L'], check=False, capture_output=True)
            subprocess.run(['xmodmap', '-e', 'keycode 134=Super_R'], check=False, capture_output=True)
            subprocess.run(['xmodmap', '-e', 'add mod4 = Super_L Super_R'], check=False, capture_output=True)
        except Exception:
            pass

    def _on_closing(self):
        """Handle window closing - restore keys"""
        self._restore_system_keys()
        return None

    def _build(self):
        rows = self.db.execute('SELECT id, name, symbol_path FROM Candidates WHERE election_id = ? AND (is_nota IS NULL OR is_nota = 0)', (self.election_id,), fetch=True)
        self.candidates = list(rows)
        self.candidates.append((-1, "NOTA", None))
        
        self._show_ballot()

    def _create_square_image(self, image_path, size=140):
        """Create a square image with consistent dimensions - contain instead of crop, preserving transparency"""
        try:
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                
                square_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                container_size = size - 20 
                
                orig_width, orig_height = img.size
                scale_factor = min(container_size / orig_width, container_size / orig_height)
                
                new_width = int(orig_width * scale_factor)
                new_height = int(orig_height * scale_factor)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                x = (size - new_width) // 2
                y = (size - new_height) // 2
                square_img.paste(img, (x, y), img) 
                
                return ImageTk.PhotoImage(square_img)
            else:
                square_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                return ImageTk.PhotoImage(square_img)
        except Exception:
            square_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            return ImageTk.PhotoImage(square_img)

    def _show_ballot(self):
        for widget in self.win.winfo_children():
            widget.destroy()
        self.candidate_buttons = []
        self.selected_candidate = None
            
        if self.awaiting_next_ballot:
            waiting_frame = tk.Frame(self.win, bg='white')
            waiting_frame.pack(expand=True, fill='both')
            
            center_frame = tk.Frame(waiting_frame, bg='white')
            center_frame.place(relx=0.5, rely=0.5, anchor='center')
            
            tk.Label(center_frame, text='BALLOT CAST', 
                    font=('Arial', 40, 'bold'), fg='#28a745', bg='white').pack(pady=(0,30))
            
            tk.Label(center_frame, text='✓', 
                    font=('Arial', 100, 'bold'), fg='#28a745', bg='white').pack(pady=30)
            
            tk.Label(center_frame, text='Waiting for voting officer...', 
                    font=('Arial', 24), fg='#343a40', bg='white').pack(pady=50)
            
            return

        title_frame = tk.Frame(self.win, bg='white', pady=TITLE_PADDING)
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text='Voting Machine', 
                font=('Arial', 50, 'bold'), fg='#343a40', bg='white').pack()

        main_frame = tk.Frame(self.win, bg='white')
        main_frame.pack(expand=True, fill='both', padx=50, pady=TITLE_TO_TABLE_SPACING)

        # Check if we need scrolling (more than 6 candidates including NOTA)
        needs_scrolling = len(self.candidates) > 6

        if needs_scrolling:
            canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
            scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            table_container = scrollable_frame
        else:
            table_container = main_frame

        table_frame = tk.Frame(table_container, bg='#e9ecef', relief='flat', bd=0)
        table_frame.pack(padx=20, pady=20, fill='x')

        border_frame = tk.Frame(table_frame, bg='#343a40', relief='flat', bd=0)
        border_frame.pack(fill='x', padx=6, pady=6)

        top_border = tk.Frame(border_frame, bg='#343a40', height=4)
        top_border.pack(fill='x', pady=0)

        for i, (cid, name, symbol_path) in enumerate(self.candidates):
            row_frame = tk.Frame(border_frame, bg='#343a40', height=4)
            row_frame.pack(fill='x', pady=4)
            
            content_row = tk.Frame(row_frame, bg='white', height=140, relief='flat', bd=0)
            content_row.pack(fill='both', expand=True, padx=4)
            content_row.pack_propagate(False)
            
            content_row.configure(width=1600)
            
            name_frame = tk.Frame(content_row, bg='white', relief='flat', bd=0, width=1000)
            name_frame.pack(side='left', fill='y', padx=(5,2))
            name_frame.pack_propagate(False)
            
            tk.Label(name_frame, text=name,
                    font=('Arial', 24), fg='#343a40', bg='white',
                    wraplength=800, justify='center').pack(expand=True)
            
            symbol_frame = tk.Frame(content_row, bg='white', relief='flat', bd=0, width=300)
            symbol_frame.pack(side='left', fill='y', padx=2)
            symbol_frame.pack_propagate(False)
            
            if cid == -1:
                nota_img = self._create_nota_symbol()
                symbol_label = tk.Label(symbol_frame, image=nota_img, bg='white')
                symbol_label.image = nota_img
            else:
                candidate_img = self._create_square_image(symbol_path)
                symbol_label = tk.Label(symbol_frame, image=candidate_img, bg='white')
                symbol_label.image = candidate_img
            
            symbol_label.pack(expand=True, pady=10)
            
            button_frame = tk.Frame(content_row, bg='white', relief='flat', bd=0, width=300)
            button_frame.pack(side='right', fill='y', padx=(2,5))
            button_frame.pack_propagate(False)
            
            vote_btn = tk.Button(button_frame, text='',
                               font=('Arial', 18, 'bold'), 
                               bg='#dc3545', fg='white',
                               relief='flat', bd=0,
                               activebackground='#c82333', activeforeground='white',
                               width=8, height=2,
                               cursor='hand2',
                               command=lambda idx=i: self._select_candidate(idx))
            vote_btn.pack(expand=True, padx=10, pady=15)
            
            self.candidate_buttons.append(vote_btn)

        def _on_mousewheel(event):
            if needs_scrolling:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        if needs_scrolling:
            canvas.bind("<MouseWheel>", _on_mousewheel)
            canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def _create_nota_symbol(self, size=140):
        """Create a standard NOTA symbol"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (size, size), 'white')
            draw = ImageDraw.Draw(img)
            
            margin = 20
            circle_bbox = [margin, margin, size-margin, size-margin]
            
            draw.ellipse(circle_bbox, outline="#000000", width=6, fill='#f8f9fa')
            
            x_margin = 36
            draw.line([x_margin, x_margin, size-x_margin, size-x_margin], fill="#000000", width=5)
            draw.line([x_margin, size-x_margin, size-x_margin, x_margin], fill="#000000", width=5)
            
            return ImageTk.PhotoImage(img)
        except Exception:
            square_img = Image.new('RGB', (size, size), "#000000")
            return ImageTk.PhotoImage(square_img)

    def _select_candidate(self, candidate_index):
        """Handle candidate selection when vote button is clicked"""
        if self.awaiting_next_ballot or self.has_voted_current_ballot:
            return
            
        self.selected_candidate = candidate_index
        
        for btn in self.candidate_buttons:
            btn.config(bg='#dc3545', activebackground='#c82333')
        
        self.candidate_buttons[candidate_index].config(bg='#28a745', activebackground='#218838')

    def _cast_vote(self, event=None):
        if self.awaiting_next_ballot or self.has_voted_current_ballot or self.selected_candidate is None:
            return 'break'
            
        candidate_id, candidate_name, _ = self.candidates[self.selected_candidate]
        
        if candidate_id == -1:
            nota_id = self.db.execute('SELECT id FROM Candidates WHERE election_id = ? AND is_nota = 1', 
                                    (self.election_id,), fetch=True)
            if not nota_id:
                nota_id = self.db.execute('INSERT INTO Candidates (election_id, name, symbol_path, is_nota) VALUES (?, ?, ?, ?)',
                                        (self.election_id, 'NOTA', None, 1))
            else:
                nota_id = nota_id[0][0]
            self.db.execute('INSERT INTO Votes (election_id, candidate_id) VALUES (?, ?)', (self.election_id, nota_id))
        else:
            self.db.execute('INSERT INTO Votes (election_id, candidate_id) VALUES (?, ?)', (self.election_id, candidate_id))
        
        play_beep_sound(800, 0.3)
        
        self.has_voted_current_ballot = True
        self.awaiting_next_ballot = True
        
        self._show_ballot()
        return 'break'

    def _next_ballot(self, event=None):
        if self.awaiting_next_ballot:
            self.has_voted_current_ballot = False
            self.awaiting_next_ballot = False
            self.selected_candidate = None
            self._show_ballot()
        return 'break'

    def _delete_last_vote(self, event=None):
        if self.awaiting_next_ballot:
            last_vote = self.db.execute('''
                SELECT id FROM Votes 
                WHERE election_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (self.election_id,), fetch=True)
            
            if last_vote:
                self.db.execute('DELETE FROM Votes WHERE id = ?', (last_vote[0][0],))
                
                play_double_beep()
            
            self.has_voted_current_ballot = False
            self.awaiting_next_ballot = False
            self.selected_candidate = None
            self._show_ballot()
        return 'break'

    def _on_key(self, event):
        if event.state & 4 and event.keysym.lower() == 'q':
            self._on_ctrl_q()
        return 'break'

    def _on_ctrl_q(self):
        pw = simpledialog.askstring('Admin Password', 'Enter admin password to end voting:', show='*', parent=self.win)
        if pw is None:
            return
        if SecurityManager.verify_password(pw, self.admin_hash):
            self._restore_system_keys()
            exporter = ResultsExporter(self.db)
            paths = exporter.export_results(self.election_id, output_dir='results')
            msg = f'Voting ended. Exported:\n• {paths[0]}\n• {paths[1]}'
            if paths[2]:
                msg += f"\n• {paths[2]}"
            messagebox.showinfo('Voting Ended', msg, parent=self.win)
            self.win.destroy()
        else:
            messagebox.showerror('Invalid', 'Incorrect password', parent=self.win)