#!/usr/bin/env python3
"""
BI Documentation Tool - Analyst GUI
Simple graphical interface for business analysts to scan BI files
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import subprocess
import json
from pathlib import Path
import webbrowser
import datetime


class BIDocGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BI Documentation Tool - Analyst Edition")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.input_files = []
        self.output_dir = tk.StringVar(value=str(Path.home() / "BI-Documentation"))
        self.format_var = tk.StringVar(value="all")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to scan BI files")
        
        self.setup_ui()
        self.center_window()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="BI Documentation Tool", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="Scan Power BI and Tableau files to generate comprehensive documentation",
                                  font=('Segoe UI', 9))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        files_frame = ttk.LabelFrame(main_frame, text="1. Select BI Files", padding="10")
        files_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        
        # File list
        self.file_listbox = tk.Listbox(files_frame, height=4, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # File buttons
        btn_frame = ttk.Frame(files_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(btn_frame, text="Add Files...", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Add Folder...", command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT)
        
        # Drag and drop hint
        self.hint_label = ttk.Label(files_frame, text="💡 Tip: You can also drag and drop files directly onto this window",
                              font=('Segoe UI', 8), foreground='gray')
        self.hint_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="2. Output Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Output directory
        ttk.Label(options_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        output_frame = ttk.Frame(options_frame)
        output_frame.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 5))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir)
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).grid(row=0, column=1)
        
        # Output format
        ttk.Label(options_frame, text="Output Format:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        ttk.Radiobutton(format_frame, text="All (Markdown + JSON)", variable=self.format_var, 
                       value="all").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Markdown only", variable=self.format_var, 
                       value="markdown").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="JSON only", variable=self.format_var, 
                       value="json").pack(side=tk.LEFT)
        
        # Action section
        action_frame = ttk.LabelFrame(main_frame, text="3. Generate Documentation", padding="10")
        action_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        action_frame.columnconfigure(0, weight=1)
        
        # Scan button
        self.scan_button = ttk.Button(action_frame, text="🔍 Scan BI Files", 
                                     command=self.start_scan, style='Accent.TButton')
        self.scan_button.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(action_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(action_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="4. Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Results buttons
        results_btn_frame = ttk.Frame(results_frame)
        results_btn_frame.grid(row=1, column=0, sticky="ew")
        
        self.open_folder_btn = ttk.Button(results_btn_frame, text="📁 Open Output Folder", 
                                         command=self.open_output_folder, state=tk.DISABLED)
        self.open_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_results_btn = ttk.Button(results_btn_frame, text="Clear Results", 
                                           command=self.clear_results)
        self.clear_results_btn.pack(side=tk.LEFT)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="📄", font=('Segoe UI', 8)).grid(row=0, column=0, padx=(0, 5))
        ttk.Label(status_frame, text="Supports: .pbix (Power BI), .twb/.twbx (Tableau)", 
                 font=('Segoe UI', 8), foreground='gray').grid(row=0, column=1, sticky="w")
        
        # Configure drag and drop
        self.setup_drag_drop()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
            # Enable drag and drop if tkinterdnd2 is available
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop_files)
            self.drag_drop_available = True
            self.log_message("✅ Drag and drop enabled (tkinterdnd2 available)")
        except ImportError:
            # tkinterdnd2 not available, show helpful message
            self.drag_drop_available = False
            self.log_message("ℹ️ Drag and drop not available. To enable: pip install tkinterdnd2")
            # Update the hint label to reflect this
            self.root.after(100, self.update_drag_drop_hint)
            
    def update_drag_drop_hint(self):
        """Update the drag and drop hint based on availability"""
        if not self.drag_drop_available:
            self.hint_label.config(text="💡 Tip: Use 'Add Files' or 'Add Folder' buttons (drag-and-drop requires: pip install tkinterdnd2)")
            
    def drop_files(self, event):
        """Handle dropped files"""
        if not hasattr(self, 'drag_drop_available') or not self.drag_drop_available:
            return
            
        files = self.root.tk.splitlist(event.data)
        valid_files = []
        
        for file_path in files:
            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.pbix', '.twb', '.twbx']:
                    valid_files.append(file_path)
                    
        if valid_files:
            self.input_files.extend(valid_files)
            self.update_file_list()
            self.log_message(f"✅ Added {len(valid_files)} file(s) via drag and drop")
        else:
            self.log_message("⚠️ No valid BI files found in dropped items")
            
    def add_files(self):
        """Add files via file dialog"""
        files = filedialog.askopenfilenames(
            title="Select BI Files",
            filetypes=[
                ("All BI Files", "*.pbix;*.twb;*.twbx"),
                ("Power BI Files", "*.pbix"),
                ("Tableau Files", "*.twb;*.twbx"),
                ("All Files", "*.*")
            ]
        )
        
        if files:
            self.input_files.extend(files)
            self.update_file_list()
            self.log_message(f"✅ Added {len(files)} file(s)")
            
    def add_folder(self):
        """Add all BI files from a folder"""
        folder = filedialog.askdirectory(title="Select Folder with BI Files")
        
        if folder:
            found_files = []
            for ext in ['*.pbix', '*.twb', '*.twbx']:
                found_files.extend(Path(folder).glob(ext))
                found_files.extend(Path(folder).glob(ext.upper()))
                
            if found_files:
                file_paths = [str(f) for f in found_files]
                self.input_files.extend(file_paths)
                self.update_file_list()
                self.log_message(f"✅ Added {len(file_paths)} file(s) from folder")
            else:
                self.log_message("⚠️ No BI files found in selected folder")
                
    def remove_files(self):
        """Remove selected files from list"""
        selected = self.file_listbox.curselection()
        if selected:
            # Remove in reverse order to maintain indices
            for index in reversed(selected):
                del self.input_files[index]
            self.update_file_list()
            self.log_message(f"🗑️ Removed {len(selected)} file(s)")
            
    def clear_files(self):
        """Clear all files from list"""
        if self.input_files:
            count = len(self.input_files)
            self.input_files.clear()
            self.update_file_list()
            self.log_message(f"🗑️ Cleared {count} file(s)")
            
    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.input_files:
            filename = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, filename)
            
    def browse_output(self):
        """Browse for output directory"""
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.output_dir.set(folder)
            
    def start_scan(self):
        """Start the scanning process"""
        if not self.input_files:
            messagebox.showwarning("No Files", "Please add some BI files to scan first.")
            return
            
        # Validate output directory
        output_path = Path(self.output_dir.get())
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Output Error", f"Cannot create output directory:\n{e}")
            return
            
        # Disable scan button and start processing
        self.scan_button.config(state=tk.DISABLED, text="🔄 Processing...")
        self.progress_var.set(0)
        self.open_folder_btn.config(state=tk.DISABLED)
        
        # Start scanning in background thread
        thread = threading.Thread(target=self.scan_files, daemon=True)
        thread.start()
        
    def scan_files(self):
        """Scan files in background thread"""
        total_files = len(self.input_files)
        successful = 0
        failed = 0
        
        self.root.after(0, lambda: self.status_var.set("Starting scan..."))
        self.root.after(0, lambda: self.log_message("🚀 Starting BI file scan..."))
        
        for i, file_path in enumerate(self.input_files):
            filename = os.path.basename(file_path)
            progress = (i / total_files) * 100
            
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda f=filename: self.status_var.set(f"Processing {f}..."))
            self.root.after(0, lambda f=filename: self.log_message(f"📊 Processing: {f}"))
            
            try:
                # Run bidoc command
                cmd = [
                    sys.executable, "-m", "bidoc",
                    "-i", file_path,
                    "-o", self.output_dir.get(),
                    "-f", self.format_var.get(),
                    "-v"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    successful += 1
                    self.root.after(0, lambda f=filename: self.log_message(f"✅ Successfully processed: {f}"))
                else:
                    failed += 1
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    self.root.after(0, lambda f=filename, e=error_msg: 
                                   self.log_message(f"❌ Failed to process {f}: {e}"))
                    
            except subprocess.TimeoutExpired:
                failed += 1
                self.root.after(0, lambda f=filename: 
                               self.log_message(f"⏰ Timeout processing {f} (file too large?)"))
            except Exception as e:
                failed += 1
                self.root.after(0, lambda f=filename, e=str(e): 
                               self.log_message(f"❌ Error processing {f}: {e}"))
                
        # Scanning complete
        self.root.after(0, lambda: self.progress_var.set(100))
        self.root.after(0, lambda: self.status_var.set(f"Complete: {successful} successful, {failed} failed"))
        self.root.after(0, lambda: self.log_message(f"🏁 Scan complete! {successful} successful, {failed} failed"))
        
        # Re-enable buttons
        self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL, text="🔍 Scan BI Files"))
        if successful > 0:
            self.root.after(0, lambda: self.open_folder_btn.config(state=tk.NORMAL))
            
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_path = Path(self.output_dir.get())
        if output_path.exists():
            if sys.platform == "win32":
                os.startfile(output_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", output_path])
            else:
                subprocess.run(["xdg-open", output_path])
        else:
            messagebox.showerror("Folder Not Found", "Output folder does not exist.")
            
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete(1.0, tk.END)
        
    def log_message(self, message):
        """Add a message to the results log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)


def main():
    """Main entry point"""
    # Check if bidoc is available
    try:
        result = subprocess.run([sys.executable, "-m", "bidoc", "--help"], 
                              capture_output=True, timeout=10)
        if result.returncode != 0:
            raise Exception("bidoc module not found")
    except Exception:
        messagebox.showerror(
            "BI Documentation Tool Not Found",
            "The BI Documentation Tool CLI is not installed or not working.\n\n"
            "Please ensure:\n"
            "1. Python is installed\n"
            "2. The BI Documentation Tool is installed\n"
            "3. All dependencies are satisfied\n\n"
            "Run 'python -m bidoc --help' in command prompt to test."
        )
        return
        
    # Create and run GUI
    root = tk.Tk()
    app = BIDocGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
