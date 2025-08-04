import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import os
from hasher import Hasher

class DuplicateRemoverGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗂️ Duplicate Files Remover")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        self.root.configure(bg="#f0f0f0")
        
        
        # Create hasher instance
        self.hasher = Hasher(chunk_size=1024 * 1024)
        self.selected_directory = tk.StringVar()
        self.is_processing = False
        self.extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.csv', '.mp3', '.wav', '.mp4', '.avi', '.mkv']

        self.setup_ui()
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Duplicate Files Remover", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Directory selection frame
        dir_frame = ttk.LabelFrame(main_frame, text="📁 Select Directory", padding="10")
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        # Directory path entry
        self.entry_dir = ttk.Entry(dir_frame, textvariable=self.selected_directory, 
                                  font=("Arial", 10), width=60)
        self.entry_dir.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Browse button
        self.btn_browse = ttk.Button(dir_frame, text="📂 Browse", 
                                    command=self.browse_directory, width=12)
        self.btn_browse.grid(row=0, column=1)
        
        # dropdown for file extensions
        
        self.extension_var = tk.StringVar(value=self.extensions)
        self.extension_dropdown = ttk.Combobox(dir_frame, textvariable=self.extension_var,
                                               values=self.extensions, state="readonly", 
                                               width=50, font=("Arial", 10))
        self.extension_dropdown.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        self.extension_dropdown.set("Select file extensions to scan")

        # Action buttons frame
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        # Scan button
        self.btn_scan = ttk.Button(action_frame, text="🔍 Scan for Duplicates", 
                                  command=self.scan_duplicates, width=20)
        self.btn_scan.grid(row=0, column=0, padx=(0, 10))

        # Stop button
        self.btn_stop = ttk.Button(action_frame, text="⏹️ Stop Scan",
                                    command=self.stop_scan, width=20)
        self.btn_stop.grid(row=0, column=2, padx=(10, 0))
        
        # Remove button
        self.btn_remove = ttk.Button(action_frame, text="🗑️ Remove Duplicates", 
                                    command=self.remove_duplicates, width=20,
                                    state="disabled")
        self.btn_remove.grid(row=0, column=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="📊 Results", padding="10")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                     height=15, font=("Consolas", 9))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to scan for duplicates")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Store duplicate groups for removal
        self.duplicate_groups = []
        
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(title="Select directory to scan for duplicates")
        if directory:
            self.selected_directory.set(directory)
            self.results_text.delete(1.0, tk.END)
            self.btn_remove.config(state="disabled")
            self.duplicate_groups = []
            self.update_status("Directory selected. Click 'Scan for Duplicates' to begin.")
            
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def scan_duplicates(self):
        """Scan for duplicate files in selected directory"""
        directory = self.selected_directory.get().strip()
        if not directory:
            messagebox.showwarning("No Directory", "Please select a directory first.")
            return
            
        if not os.path.exists(directory):
            messagebox.showerror("Invalid Directory", "The selected directory does not exist.")
            return
            
        # Disable buttons and start progress
        self.set_processing_state(True)
        self.results_text.delete(1.0, tk.END)
        
        # Run scan in separate thread to prevent UI freezing
        # use many threads to handle long-running tasks
        self.update_status("Scanning for duplicates... Please wait.")
        threading.Thread(target=self._scan_worker, args=(directory,), daemon=True).start()
    
    def stop_scan(self):
        """Stop the current scan if running"""
        if self.is_processing:
            self.set_processing_state(False)
            self.update_status("Scan stopped by user.")
            messagebox.showinfo("Scan Stopped", "The scan has been stopped.")
        else:
            messagebox.showinfo("No Scan Running", "No scan is currently in progress.")



    def _scan_worker(self, directory):
        """Worker function for scanning duplicates"""
        try:
            self.update_status("Scanning files by size...")
            # send the chosen extension to the hasher 

            duplicates_on_size = self.hasher.find_duplicates_on_size(directory, self.extension_var.get().split(','))
        
            if not duplicates_on_size:
                self.root.after(0, self._scan_complete, [], "No duplicate files found based on size, no duplicates found.")
                return
                
            self.update_status("Analyzing file contents for similar content on equal size...")
            duplicates_on_hash = self.hasher.hash_duplicates(duplicates_on_size)
            
            self.root.after(0, self._scan_complete, duplicates_on_hash, None)
            
        except Exception as e:
            self.root.after(0, self._scan_error, str(e))
            
    def _scan_complete(self, duplicate_groups, message):
        """Handle scan completion"""
        self.duplicate_groups = duplicate_groups
        self.set_processing_state(False)
        
        if message:
            self.results_text.insert(tk.END, f"{message}\n")
            self.update_status("Scan complete - No duplicates found")
            return
            
        if duplicate_groups:
            total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
            self.results_text.insert(tk.END, f"Found {len(duplicate_groups)} groups of duplicate files:\n")
            self.results_text.insert(tk.END, f"Total duplicate files: {total_duplicates}\n\n")
            
            for i, group in enumerate(duplicate_groups, 1):
                self.results_text.insert(tk.END, f"Group {i} ({len(group)} files):\n")
                self.results_text.insert(tk.END, f"  📄 Original: {group[0]}\n")
                for duplicate in group[1:]:
                    self.results_text.insert(tk.END, f"  🗑️ Duplicate: {duplicate}\n")
                self.results_text.insert(tk.END, "\n")
                
            self.btn_remove.config(state="normal")
            self.update_status(f"Scan complete - Found {total_duplicates} duplicate files")
        else:
            self.results_text.insert(tk.END, "No duplicate files found.\n")
            self.update_status("Scan complete - No duplicates found")
            
    def _scan_error(self, error_message):
        """Handle scan error"""
        self.set_processing_state(False)
        messagebox.showerror("Scan Error", f"An error occurred while scanning:\n{error_message}")
        self.update_status("Scan failed")
        
    def remove_duplicates(self):
        """Remove duplicate files"""
        if not self.duplicate_groups:
            messagebox.showwarning("No Duplicates", "No duplicates found. Please scan first.")
            return
            
        total_duplicates = sum(len(group) - 1 for group in self.duplicate_groups)
        
        # Confirm removal
        response = messagebox.askyesno(
            "Confirm Removal",
            f"This will permanently delete {total_duplicates} duplicate files.\n\n"
            "The first file in each group will be kept as the original.\n"
            "Are you sure you want to continue?"
        )
        
        if not response:
            return
            
        # Start removal process
        self.set_processing_state(True)
        threading.Thread(target=self._remove_worker, daemon=True).start()
        
    def _remove_worker(self):
        """Worker function for removing duplicates"""
        try:
            removed_files = []
            failed_removals = []
            
            for group in self.duplicate_groups:
                # Keep the first file, remove the rest
                for file_path in group[1:]:
                    try:
                        os.remove(file_path)
                        removed_files.append(file_path)
                        self.update_status(f"Removed: {os.path.basename(file_path)}")
                    except Exception as e:
                        failed_removals.append((file_path, str(e)))
                        
            self.root.after(0, self._remove_complete, removed_files, failed_removals)
            
        except Exception as e:
            self.root.after(0, self._remove_error, str(e))
            
    def _remove_complete(self, removed_files, failed_removals):
        """Handle removal completion"""
        self.set_processing_state(False)
        
        # Update results
        self.results_text.delete(1.0, tk.END)
        
        if removed_files:
            self.results_text.insert(tk.END, f"✅ Successfully removed {len(removed_files)} duplicate files:\n\n")
            for file_path in removed_files:
                self.results_text.insert(tk.END, f"  🗑️ {file_path}\n")
                
        if failed_removals:
            self.results_text.insert(tk.END, f"\n❌ Failed to remove {len(failed_removals)} files:\n\n")
            for file_path, error in failed_removals:
                self.results_text.insert(tk.END, f"  ❌ {file_path}: {error}\n")
                
        if not removed_files and not failed_removals:
            self.results_text.insert(tk.END, "No files were removed.\n")
            
        # Reset state
        self.duplicate_groups = []
        self.btn_remove.config(state="disabled")
        
        success_count = len(removed_files)
        self.update_status(f"Removal complete - {success_count} files removed")
        
        if success_count > 0:
            messagebox.showinfo("Removal Complete", 
                              f"Successfully removed {success_count} duplicate files!")
                              
    def _remove_error(self, error_message):
        """Handle removal error"""
        self.set_processing_state(False)
        messagebox.showerror("Removal Error", f"An error occurred during removal:\n{error_message}")
        self.update_status("Removal failed")
        
    def set_processing_state(self, processing):
        """Enable/disable UI elements during processing"""
        self.is_processing = processing
        
        if processing:
            self.btn_browse.config(state="disabled")
            self.btn_scan.config(state="disabled")
            self.btn_remove.config(state="disabled")
            self.progress.start(10)
        else:
            self.btn_browse.config(state="normal")
            self.btn_scan.config(state="normal")
            self.progress.stop()
            
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = DuplicateRemoverGUI()
    app.run()
