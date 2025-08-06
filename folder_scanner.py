import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import subprocess
import sys
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import psutil

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
        self.scan_queue = queue.Queue()
        self.max_workers = min(8, os.cpu_count() or 4)  # Limit concurrent threads
        
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
    
    def get_folder_size_fast(self, folder_path, max_depth=3, timeout=30):
        """Fast folder size calculation with optimizations"""
        total_size = 0
        start_time = time.time()

        try:
            # Use os.scandir for faster directory listing
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    # Check timeout to avoid hanging on large folders
                    if time.time() - start_time > timeout:
                        break

                    try:
                        if entry.is_file(follow_symlinks=False):
                            total_size += entry.stat().st_size
                        elif entry.is_dir(follow_symlinks=False) and max_depth > 0:
                            # Recursively scan subdirectories with depth limit
                            total_size += self.get_folder_size_fast(
                                entry.path, max_depth - 1, timeout - (time.time() - start_time)
                            )
                    except (OSError, IOError, PermissionError):
                        continue
        except (OSError, IOError, PermissionError):
            pass

        return total_size

    def get_folder_size_estimate(self, folder_path):
        """Quick folder size estimate using sampling"""
        try:
            # For very large folders, estimate size by sampling
            total_size = 0
            file_count = 0
            sample_size = 0
            max_samples = 1000  # Limit samples for speed

            with os.scandir(folder_path) as entries:
                for entry in entries:
                    if file_count >= max_samples:
                        break

                    try:
                        if entry.is_file(follow_symlinks=False):
                            size = entry.stat().st_size
                            total_size += size
                            sample_size += size
                            file_count += 1
                        elif entry.is_dir(follow_symlinks=False):
                            # Quick check of subdirectory
                            try:
                                with os.scandir(entry.path) as sub_entries:
                                    for sub_entry in sub_entries:
                                        if file_count >= max_samples:
                                            break
                                        if sub_entry.is_file(follow_symlinks=False):
                                            size = sub_entry.stat().st_size
                                            total_size += size
                                            file_count += 1
                            except (OSError, IOError, PermissionError):
                                continue
                    except (OSError, IOError, PermissionError):
                        continue

            return total_size
        except (OSError, IOError, PermissionError):
            return 0
    
    def scan_single_folder(self, folder_path):
        """Scan a single folder and return its size"""
        try:
            # Use fast estimation for very large folders
            size = self.get_folder_size_estimate(folder_path)
            return folder_path, size
        except Exception:
            return folder_path, 0

    def get_drives_fast(self):
        """Get available drives using psutil for better performance"""
        drives = []
        try:
            # Use psutil for faster drive detection
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if os.name == 'nt' and partition.fstype:  # Windows with valid filesystem
                    drives.append(partition.mountpoint)
                elif os.name != 'nt':  # Unix-like systems
                    drives.append(partition.mountpoint)
        except:
            # Fallback to old method
            if os.name == 'nt':
                import string
                for letter in string.ascii_uppercase:
                    drive = f"{letter}:\\"
                    if os.path.exists(drive):
                        drives.append(drive)
            else:
                drives = ['/']

        return drives

    def get_top_level_folders(self, drives):
        """Get all top-level folders from all drives"""
        folders = []
        for drive in drives:
            try:
                with os.scandir(drive) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False):
                            folders.append(entry.path)
            except (OSError, IOError, PermissionError):
                continue
        return folders

    def scan_folders(self):
        """Fast parallel scan of all drives for largest folders"""
        try:
            self.folder_data = []

            # Get drives quickly
            self.update_status("Detecting drives...")
            drives = self.get_drives_fast()
            self.update_status(f"Found {len(drives)} drives")

            # Get all top-level folders quickly
            self.update_status("Finding folders...")
            folders = self.get_top_level_folders(drives)
            self.update_status(f"Found {len(folders)} folders to scan")

            if not folders:
                self.root.after(0, self.update_results, [])
                return

            # Use ThreadPoolExecutor for parallel scanning
            folder_sizes = {}
            completed = 0

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all folder scan tasks
                future_to_folder = {
                    executor.submit(self.scan_single_folder, folder): folder
                    for folder in folders
                }

                # Process completed tasks
                for future in as_completed(future_to_folder):
                    try:
                        folder_path, size = future.result(timeout=60)  # 60 second timeout per folder
                        if size > 0:
                            folder_sizes[folder_path] = size

                        completed += 1
                        progress = (completed / len(folders)) * 100
                        self.update_status(f"Scanned {completed}/{len(folders)} folders ({progress:.1f}%)")

                    except Exception as e:
                        completed += 1
                        continue

            # Get top 5 largest folders
            if folder_sizes:
                sorted_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:5]
                self.root.after(0, self.update_results, sorted_folders)
            else:
                self.root.after(0, self.update_results, [])

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
