import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import tempfile
from datetime import datetime
import webbrowser

from email_verifier import EmailVerifier
from csv_processor import CSVProcessor

class EmailVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Verifier Pro")
        self.root.geometry("800x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.email_verifier = EmailVerifier(max_workers=20, fast_mode=True, timeout=5)
        self.csv_processor = CSVProcessor()
        
        # Variables
        self.selected_files = []  # List of file paths
        self.verification_results = []
        self.is_verifying = False
        self.verification_thread = None
        self.current_file_index = 0
        self.total_files = 0
        
        # Create temp directory for downloads
        self.temp_dir = tempfile.mkdtemp()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        file_frame.columnconfigure(1, weight=1)
        
        # File selection buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected_file).pack(side=tk.LEFT)
        
        # File list
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # File listbox with scrollbar
        self.files_listbox = tk.Listbox(list_frame, height=4, selectmode=tk.SINGLE)
        files_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        # Bind selection event
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_selection_change)
        
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # File info section
        self.file_info_label = ttk.Label(file_frame, text="No files selected")
        self.file_info_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # Verification settings
        settings_frame = ttk.LabelFrame(main_frame, text="Verification Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Worker count setting
        ttk.Label(settings_frame, text="Max concurrent workers:").grid(row=0, column=0, sticky=tk.W)
        self.workers_var = tk.StringVar(value="20")
        workers_spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, textvariable=self.workers_var, width=10)
        workers_spinbox.grid(row=0, column=1, padx=(10, 0))
        
        # Fast mode setting
        self.fast_mode_var = tk.BooleanVar(value=True)
        fast_mode_check = ttk.Checkbutton(settings_frame, text="Fast Mode (faster but less thorough)", 
                                         variable=self.fast_mode_var)
        fast_mode_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Timeout setting
        ttk.Label(settings_frame, text="SMTP Timeout (seconds):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.timeout_var = tk.StringVar(value="5")
        timeout_spinbox = ttk.Spinbox(settings_frame, from_=1, to=30, textvariable=self.timeout_var, width=10)
        timeout_spinbox.grid(row=2, column=1, padx=(10, 0), pady=(10, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Verification Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to start verification")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="Start Verification", 
                                      command=self.start_verification, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                       command=self.cancel_verification, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Verification Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1) 
        main_frame.rowconfigure(5, weight=1)
        
        # Set maximum height for results frame
        results_frame.configure(height=200)
        results_frame.pack_propagate(False)
        
        # Results treeview
        columns = ('Email', 'Format', 'MX', 'Ping', 'Status', 'Source File')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=3)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == 'Email':
                self.results_tree.column(col, width=200)
            elif col == 'Source File':
                self.results_tree.column(col, width=150)
            else:
                self.results_tree.column(col, width=80)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Download section
        download_frame = ttk.LabelFrame(main_frame, text="Download Results", padding="10")
        download_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.download_all_btn = ttk.Button(download_frame, text="Download All Leads", 
                                          command=lambda: self.download_results("all_leads"), state=tk.DISABLED)
        self.download_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_valid_btn = ttk.Button(download_frame, text="Download Valid Only", 
                                            command=lambda: self.download_results("valid_only"), state=tk.DISABLED)
        self.download_valid_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_risky_btn = ttk.Button(download_frame, text="Download Risky Only", 
                                            command=lambda: self.download_results("risky_only"), state=tk.DISABLED)
        self.download_risky_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.download_valid_risky_btn = ttk.Button(download_frame, text="Download Valid + Risky", 
                                                   command=lambda: self.download_results("valid_and_risky"), state=tk.DISABLED)
        self.download_valid_risky_btn.pack(side=tk.LEFT)
        
        
    def on_file_selection_change(self, event):
        """Handle file selection change in the listbox"""
        self.validate_selected_file()
    
    def add_files(self):
        """Open file dialog to select multiple CSV/Excel files"""
        file_paths = filedialog.askopenfilenames(
            title="Select CSV/Excel files",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_listbox.insert(tk.END, file_path)
        
        self.update_file_info()
    
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files.clear()
        self.files_listbox.delete(0, tk.END)
        self.update_file_info()
    
    def remove_selected_file(self):
        """Remove the selected file from the list"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            file_path = self.files_listbox.get(index)
            self.selected_files.remove(file_path)
            self.files_listbox.delete(index)
            self.update_file_info()
    
    def update_file_info(self):
        """Update file information display"""
        if not self.selected_files:
            self.file_info_label.config(text="No files selected", foreground='black')
            self.start_button.config(state=tk.DISABLED)
            return
        
        total_emails = 0
        total_size = 0
        valid_files = 0
        
        for file_path in self.selected_files:
            try:
                is_valid, message = self.csv_processor.validate_file(file_path)
                if is_valid:
                    file_info = self.csv_processor.get_file_info(file_path)
                    total_emails += file_info['total_emails']
                    total_size += file_info['file_size']
                    valid_files += 1
            except:
                pass
        
        if valid_files > 0:
            info_text = f"✓ {valid_files} files selected | Total emails: {total_emails:,} | Total size: {total_size:,} bytes"
            self.file_info_label.config(text=info_text, foreground='green')
            self.start_button.config(state=tk.NORMAL)
        else:
            info_text = f"✗ No valid files selected"
            self.file_info_label.config(text=info_text, foreground='red')
            self.start_button.config(state=tk.DISABLED)
    
    def browse_file(self):
        """Open file dialog to select CSV/Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV/Excel file",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_listbox.insert(tk.END, file_path)
                self.update_file_info()
    
    def validate_selected_file(self):
        """Validate the selected file and show info"""
        if not self.files_listbox.curselection():
            self.file_info_label.config(text="No file selected")
            self.start_button.config(state=tk.DISABLED)
            return
        
        file_path = self.files_listbox.get(self.files_listbox.curselection()[0])
        
        try:
            is_valid, message = self.csv_processor.validate_file(file_path)
            if is_valid:
                file_info = self.csv_processor.get_file_info(file_path)
                info_text = f"✓ {message} | File size: {file_info['file_size']:,} bytes"
                self.file_info_label.config(text=info_text, foreground='green')
                self.start_button.config(state=tk.NORMAL)
            else:
                self.file_info_label.config(text=f"✗ {message}", foreground='red')
                self.start_button.config(state=tk.DISABLED)
        except Exception as e:
            self.file_info_label.config(text=f"✗ Error: {str(e)}", foreground='red')
            self.start_button.config(state=tk.DISABLED)
    
    def start_verification(self):
        """Start the email verification process for all selected files"""
        if self.is_verifying:
            return
        
        if not self.selected_files:
            messagebox.showerror("Error", "Please select files first")
            return
        
        try:
            # Collect all emails from all files
            all_emails = []
            file_emails_map = {}  # Track which emails came from which file
            
            for file_path in self.selected_files:
                try:
                    df, email_column = self.csv_processor.read_csv_file(file_path)
                    emails = self.csv_processor.extract_emails(df, email_column)
                    
                    # Add file source information
                    for email in emails:
                        if email not in file_emails_map:
                            file_emails_map[email] = file_path
                            all_emails.append(email)
                    
                except Exception as e:
                    messagebox.showwarning("Warning", f"Could not read file {file_path}: {str(e)}")
                    continue
            
            if not all_emails:
                messagebox.showerror("Error", "No valid emails found in any of the selected files")
                return
            
            # Update UI state
            self.is_verifying = True
            self.start_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.NORMAL)
            self.progress_bar.config(maximum=len(all_emails))
            self.progress_bar.config(value=0)
            
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Start verification in separate thread
            self.verification_thread = threading.Thread(
                target=self.run_verification,
                args=(all_emails, file_emails_map)
            )
            self.verification_thread.daemon = True
            self.verification_thread.start()
            
            self.status_var.set(f"Verifying {len(all_emails)} emails from {len(self.selected_files)} files...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start verification: {str(e)}")
            self.reset_ui_state()
    
    def run_verification(self, emails, file_emails_map):
        """Run the verification process in background thread"""
        try:
            # Update worker count
            self.email_verifier.max_workers = int(self.workers_var.get())
            self.email_verifier.fast_mode = self.fast_mode_var.get()
            self.email_verifier.timeout = int(self.timeout_var.get())
            
            # Start verification with progress callback
            results = self.email_verifier.verify_emails_batch(
                emails, 
                progress_callback=self.update_progress
            )
            
            # Update results in main thread
            self.root.after(0, self.verification_completed, results, file_emails_map)
            
        except Exception as e:
            self.root.after(0, self.verification_error, str(e))
    
    def update_progress(self, current, total):
        """Update progress bar and label"""
        self.root.after(0, self._update_progress_ui, current, total)
    
    def _update_progress_ui(self, current, total):
        """Update progress UI elements (called in main thread)"""
        self.progress_bar.config(value=current)
        percentage = (current / total) * 100
        self.progress_label.config(text=f"Processing: {current}/{total} ({percentage:.1f}%)")
        
        # Update status
        self.status_var.set(f"Verifying emails... {current}/{total}")
    
    def verification_completed(self, results, file_emails_map):
        """Handle verification completion"""
        self.verification_results = results
        self.is_verifying = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Verification completed!")
        
        # Populate results tree
        for result in results:
            email_source = file_emails_map.get(result['email'], 'N/A')
            # Extract just the filename for display
            source_filename = os.path.basename(email_source) if email_source != 'N/A' else 'N/A'
            self.results_tree.insert('', 'end', values=(
                result['email'],
                '✓' if result['format'] else '✗',
                '✓' if result['mx'] else '✗',
                result['ping'],
                result['status'],
                source_filename
            ))
        
        # Enable download buttons
        self.download_all_btn.config(state=tk.NORMAL)
        self.download_valid_btn.config(state=tk.NORMAL)
        self.download_risky_btn.config(state=tk.NORMAL)
        self.download_valid_risky_btn.config(state=tk.NORMAL)
        
        # Show completion message with file statistics
        valid_count = sum(1 for r in results if r['status'] == 'valid')
        risky_count = sum(1 for r in results if r['status'] == 'risky')
        invalid_count = sum(1 for r in results if r['status'] == 'invalid')
        
        # Count emails per file
        file_stats = {}
        for result in results:
            source_file = file_emails_map.get(result['email'], 'Unknown')
            if source_file not in file_stats:
                file_stats[source_file] = {'total': 0, 'valid': 0, 'risky': 0, 'invalid': 0}
            file_stats[source_file]['total'] += 1
            file_stats[source_file][result['status']] += 1
        
        # Create detailed completion message
        message = f"Verification completed!\n\n"
        message += f"Total emails: {len(results)}\n"
        message += f"Valid: {valid_count}\n"
        message += f"Risky: {risky_count}\n"
        message += f"Invalid: {invalid_count}\n\n"
        message += f"Files processed: {len(self.selected_files)}\n"
        
        for file_path in self.selected_files:
            filename = os.path.basename(file_path)
            if file_path in file_stats:
                stats = file_stats[file_path]
                message += f"\n{filename}:\n"
                message += f"  Total: {stats['total']}, Valid: {stats['valid']}, Risky: {stats['risky']}, Invalid: {stats['invalid']}"
        
        self.status_var.set(f"Completed! {len(self.selected_files)} files, {len(results)} emails")
        
        messagebox.showinfo("Verification Complete", message)
    
    def verification_error(self, error_message):
        """Handle verification error"""
        self.reset_ui_state()
        messagebox.showerror("Verification Error", f"Verification failed: {error_message}")
    
    def cancel_verification(self):
        """Cancel the current verification process"""
        if self.is_verifying:
            self.email_verifier.cancel_verification()
            self.progress_label.config(text="Cancelling...")
            self.status_var.set("Cancelling verification...")
    
    def reset_ui_state(self):
        """Reset UI to initial state"""
        self.is_verifying = False
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.progress_bar.config(value=0)
        self.progress_label.config(text="Ready to start verification")
        self.status_var.set("Ready")
    
    def download_results(self, result_type):
        """Download verification results as CSV"""
        if not self.verification_results:
            messagebox.showerror("Error", "No results to download")
            return
        
        try:
            # Generate CSV content
            csv_content = self.email_verifier.generate_csv_links(self.verification_results)[result_type]
            
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_verification_{result_type}_{timestamp}.csv"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            # Open file location
            if messagebox.askyesno("Download Complete", 
                                  f"Results saved to:\n{file_path}\n\nOpen file location?"):
                os.startfile(self.temp_dir)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download results: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_verifying:
            if messagebox.askyesno("Quit", "Verification is in progress. Are you sure you want to quit?"):
                self.email_verifier.cancel_verification()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = EmailVerifierApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
