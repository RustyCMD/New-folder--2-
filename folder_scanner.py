import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import subprocess
import sys
from pathlib import Path
import time

class FolderScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Size Scanner - Find Largest Folders")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configure dark theme
        self.setup_dark_theme()
        
        # Variables
        self.scanning = False
        self.folder_data = []
        
        # Create GUI
        self.create_widgets()
        
    def setup_dark_theme(self):
        """Configure dark theme colors and styles"""
        # Dark theme colors
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'select_bg': '#404040',
            'button_bg': '#404040',
            'button_fg': '#ffffff',
            'entry_bg': '#404040',
            'entry_fg': '#ffffff',
            'progress_bg': '#404040',
            'accent': '#0078d4'
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for dark theme
        style.configure('Dark.TFrame', background=self.colors['bg'])
        style.configure('Dark.TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Dark.TButton', background=self.colors['button_bg'], foreground=self.colors['button_fg'])
        style.map('Dark.TButton', background=[('active', self.colors['accent'])])
        style.configure('Dark.Treeview', background=self.colors['select_bg'], foreground=self.colors['fg'], 
                       fieldbackground=self.colors['select_bg'])
        style.configure('Dark.Treeview.Heading', background=self.colors['button_bg'], foreground=self.colors['fg'])
        style.configure('Dark.Horizontal.TProgressbar', background=self.colors['accent'])
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Folder Size Scanner", 
                               font=('Segoe UI', 16, 'bold'), style='Dark.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Control frame
        control_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Scan button
        self.scan_button = ttk.Button(control_frame, text="Scan for Largest Folders", 
                                     command=self.start_scan, style='Dark.TButton')
        self.scan_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        self.refresh_button = ttk.Button(control_frame, text="Refresh", 
                                        command=self.refresh_scan, style='Dark.TButton')
        self.refresh_button.pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate', 
                                       style='Dark.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to scan", 
                                     style='Dark.TLabel')
        self.status_label.pack()
        
        # Results frame
        results_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for results
        columns = ('Path', 'Size', 'Action')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', 
                                style='Dark.Treeview')
        
        # Configure columns
        self.tree.heading('Path', text='Folder Path')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Action', text='Action')
        
        self.tree.column('Path', width=500, minwidth=300)
        self.tree.column('Size', width=150, minwidth=100)
        self.tree.column('Action', width=100, minwidth=80)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
    def format_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.2f} {size_names[i]}"
    
    def get_folder_size(self, folder_path):
        """Calculate total size of a folder"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    try:
                        file_path = os.path.join(dirpath, filename)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue
        except (OSError, IOError):
            pass
        return total_size
    
    def scan_folders(self):
        """Scan all drives for largest folders"""
        try:
            self.folder_data = []
            drives = []
            
            # Get all available drives on Windows
            if os.name == 'nt':
                import string
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        drives.append(drive)
            else:
                drives = ['/']
            
            self.update_status(f"Scanning {len(drives)} drives...")
            
            folder_sizes = {}
            
            for drive in drives:
                self.update_status(f"Scanning drive {drive}...")
                try:
                    for item in os.listdir(drive):
                        item_path = os.path.join(drive, item)
                        if os.path.isdir(item_path):
                            try:
                                size = self.get_folder_size(item_path)
                                if size > 0:
                                    folder_sizes[item_path] = size
                                    self.update_status(f"Scanned: {item_path}")
                            except (OSError, IOError, PermissionError):
                                continue
                except (OSError, IOError, PermissionError):
                    continue
            
            # Get top 5 largest folders
            sorted_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Update GUI with results
            self.root.after(0, self.update_results, sorted_folders)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Error during scan: {str(e)}")
        finally:
            self.root.after(0, self.scan_complete)
    
    def update_status(self, message):
        """Update status label from background thread"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def update_results(self, folders):
        """Update the results treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new results
        for i, (path, size) in enumerate(folders, 1):
            formatted_size = self.format_size(size)
            self.tree.insert('', 'end', values=(path, formatted_size, 'Open Folder'))
            self.folder_data.append(path)
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
    
    def scan_complete(self):
        """Called when scan is complete"""
        self.scanning = False
        self.scan_button.config(text="Scan for Largest Folders", state='normal')
        self.refresh_button.config(state='normal')
        self.progress.stop()
        self.status_label.config(text="Scan complete")
    
    def start_scan(self):
        """Start the folder scanning process"""
        if self.scanning:
            return
        
        self.scanning = True
        self.scan_button.config(text="Scanning...", state='disabled')
        self.refresh_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Starting scan...")
        
        # Start scanning in background thread
        thread = threading.Thread(target=self.scan_folders, daemon=True)
        thread.start()
    
    def refresh_scan(self):
        """Refresh the scan"""
        self.start_scan()
    
    def on_item_double_click(self, event):
        """Handle double-click on treeview item"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            folder_path = item['values'][0]
            self.open_folder(folder_path)
    
    def open_folder(self, folder_path):
        """Open folder in system file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")

def main():
    root = tk.Tk()
    app = FolderScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
