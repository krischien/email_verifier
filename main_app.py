import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import tempfile
from datetime import datetime
import webbrowser

from email_verifier import EmailVerifier
from csv_processor import CSVProcessor
from email_sender import EmailSender, EMAIL_PROVIDERS
from ai_message_creator import AIMessageCreator, EMAIL_TEMPLATES, INDUSTRY_TEMPLATES

class MailCommanderProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mail Commander Pro")
        self.root.geometry("800x845")
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
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Create tabs
        self.verification_tab = ttk.Frame(self.notebook)
        self.email_sender_tab = ttk.Frame(self.notebook)
        self.ai_creator_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.verification_tab, text="Email Verification")
        self.notebook.add(self.ai_creator_tab, text="AI Message Creator")
        self.notebook.add(self.email_sender_tab, text="Campaign Commander")
        
        # Setup verification tab
        self.setup_verification_tab()
        
        # Setup email sender tab
        self.setup_email_sender_tab()
        
        # Setup AI creator tab
        self.setup_ai_creator_tab()
        
    def setup_verification_tab(self):
        """Setup the email verification tab"""
        # Configure grid weights for verification tab
        self.verification_tab.columnconfigure(0, weight=1)
        self.verification_tab.rowconfigure(5, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(self.verification_tab, text="File Selection", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
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
        settings_frame = ttk.LabelFrame(self.verification_tab, text="Verification Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
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
        progress_frame = ttk.LabelFrame(self.verification_tab, text="Verification Progress", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
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
        button_frame = ttk.Frame(self.verification_tab)
        button_frame.grid(row=3, column=0, pady=(0, 20))
        
        self.start_button = ttk.Button(button_frame, text="Start Verification", 
                                       command=self.start_verification, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                        command=self.cancel_verification, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT)
        
        # Results section
        results_frame = ttk.LabelFrame(self.verification_tab, text="Verification Results", padding="10")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1) 
        
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
        download_frame = ttk.LabelFrame(self.verification_tab, text="Download Results", padding="10")
        download_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
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
        
        
    def setup_email_sender_tab(self):
        """Setup the email sender tab"""
        # Configure grid weights for email sender tab
        self.email_sender_tab.columnconfigure(0, weight=1)
        
        # Email sender frame
        sender_frame = ttk.LabelFrame(self.email_sender_tab, text="Campaign Commander", padding="10")
        sender_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Provider selection
        provider_frame = ttk.Frame(sender_frame)
        provider_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(provider_frame, text="Email Provider:").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value="gmail")
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.provider_var, 
                                     values=list(EMAIL_PROVIDERS.keys()), state="readonly", width=15)
        provider_combo.pack(side=tk.LEFT, padx=(10, 0))
        provider_combo.bind('<<ComboboxSelected>>', self.on_provider_change)
        
        # Connection settings
        settings_frame = ttk.Frame(sender_frame)
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Row 1: SMTP Server and Port
        ttk.Label(settings_frame, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W)
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        ttk.Entry(settings_frame, textvariable=self.smtp_server_var, width=25).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(settings_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.smtp_port_var = tk.StringVar(value="587")
        ttk.Entry(settings_frame, textvariable=self.smtp_port_var, width=8).grid(row=0, column=3, padx=(10, 0))
        
        # Row 2: Username and Password
        ttk.Label(settings_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.username_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.username_var, width=25).grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(settings_frame, text="Password:").grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        self.password_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.password_var, show="*", width=25).grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        
        # Row 3: Security and Rate settings
        self.use_tls_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Use TLS", variable=self.use_tls_var).grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        self.use_ssl_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Use SSL", variable=self.use_ssl_var).grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(settings_frame, text="Rate Limit (emails/min):").grid(row=2, column=2, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        self.rate_limit_var = tk.StringVar(value="60")
        ttk.Entry(settings_frame, textvariable=self.rate_limit_var, width=8).grid(row=2, column=3, padx=(10, 0), pady=(10, 0))
        
        # Test connection button
        test_frame = ttk.Frame(sender_frame)
        test_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(test_frame, text="Test Connection", command=self.test_email_connection).pack(side=tk.LEFT)
        self.connection_status_label = ttk.Label(test_frame, text="", foreground='black')
        self.connection_status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Email content section
        content_frame = ttk.LabelFrame(sender_frame, text="Email Content", padding="10")
        content_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Subject
        ttk.Label(content_frame, text="Subject:").grid(row=0, column=0, sticky=tk.W)
        self.subject_var = tk.StringVar(value="Hello {name}!")
        ttk.Entry(content_frame, textvariable=self.subject_var, width=50).grid(row=0, column=1, padx=(10, 0))
        
        # Body
        ttk.Label(content_frame, text="Body:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.body_text = tk.Text(content_frame, height=6, width=50)
        self.body_text.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        self.body_text.insert(tk.END, "Hello {name},\n\nThis is a test email from Mail Commander Pro.\n\nBest regards,\nYour Team")
        
        # Send buttons
        send_frame = ttk.Frame(sender_frame)
        send_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.send_to_valid_btn = ttk.Button(send_frame, text="Send to Valid Emails", 
                                           command=lambda: self.send_campaign("valid"), state=tk.DISABLED)
        self.send_to_valid_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.send_to_valid_risky_btn = ttk.Button(send_frame, text="Send to Valid + Risky", 
                                                 command=lambda: self.send_campaign("valid_and_risky"), state=tk.DISABLED)
        self.send_to_valid_risky_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress frame for email sending
        email_progress_frame = ttk.Frame(sender_frame)
        email_progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(email_progress_frame, text="Email Progress:").grid(row=0, column=0, sticky=tk.W)
        self.email_progress_var = tk.DoubleVar()
        self.email_progress_bar = ttk.Progressbar(email_progress_frame, variable=self.email_progress_var, 
                                                 maximum=100, length=300)
        self.email_progress_bar.grid(row=0, column=1, padx=(10, 0))
        
        self.email_progress_label = ttk.Label(email_progress_frame, text="Ready to send")
        self.email_progress_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Cancel button for email sending
        self.cancel_email_btn = ttk.Button(email_progress_frame, text="Cancel Sending", 
                                          command=self.cancel_email_sending, state=tk.DISABLED)
        self.cancel_email_btn.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Status indicator for email sender
        status_frame = ttk.Frame(sender_frame)
        status_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.email_sender_status_label = ttk.Label(status_frame, text="⚠️ Please verify emails first in the Email Verification tab", 
                                                  foreground='orange', font=('Arial', 9))
        self.email_sender_status_label.pack(side=tk.LEFT)
        
    def on_provider_change(self, event):
        """Handle email provider change"""
        provider = self.provider_var.get()
        if provider in EMAIL_PROVIDERS:
            config = EMAIL_PROVIDERS[provider]
            self.smtp_server_var.set(config['smtp_server'])
            self.smtp_port_var.set(str(config['smtp_port']))
            self.use_tls_var.set(config['use_tls'])
            self.use_ssl_var.set(config['use_ssl'])
            self.rate_limit_var.set(str(config['rate_limit']))
        
    def test_email_connection(self):
        """Test the email connection settings"""
        config = self.get_email_config()
        if not config['username'] or not config['password']:
            self.connection_status_label.config(text="Please enter username and password", foreground='red')
            return
        
        try:
            sender = EmailSender(config)
            result = sender.test_connection()
            
            if result['status'] == 'success':
                self.connection_status_label.config(text=result['message'], foreground='green')
            else:
                self.connection_status_label.config(text=result['message'], foreground='red')
                
        except Exception as e:
            self.connection_status_label.config(text=f"Connection error: {str(e)}", foreground='red')
    
    def get_email_config(self):
        """Get email configuration from UI"""
        return {
            'smtp_server': self.smtp_server_var.get(),
            'smtp_port': int(self.smtp_port_var.get()),
            'username': self.username_var.get(),
            'password': self.password_var.get(),
            'use_tls': self.use_tls_var.get(),
            'use_ssl': self.use_ssl_var.get(),
            'rate_limit': int(self.rate_limit_var.get()),
            'delay_between': 60.0 / int(self.rate_limit_var.get()) if int(self.rate_limit_var.get()) > 0 else 1
        }
    
    def send_campaign(self, target_type):
        """Send email campaign to specified email types"""
        if not self.verification_results:
            messagebox.showerror("Error", "Please verify emails first")
            return
        
        # Filter emails based on target type
        if target_type == "valid":
            target_emails = [r for r in self.verification_results if r['status'] == 'valid']
        elif target_type == "valid_and_risky":
            target_emails = [r for r in self.verification_results if r['status'] in ['valid', 'risky']]
        else:
            return
        
        if not target_emails:
            messagebox.showerror("Error", f"No {target_type} emails found")
            return
        
        # Get email content
        subject = self.subject_var.get()
        body = self.body_text.get("1.0", tk.END).strip()
        
        # Get configuration
        config = self.get_email_config()
        if not config['username'] or not config['password']:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        # Create email sender
        try:
            self.email_sender = EmailSender(config)
            
            # Prepare email list
            emails_to_send = []
            for result in target_emails:
                email_data = {'email': result['email']}
                # Try to extract name from source file if available
                if 'source_file' in result:
                    # You could add logic here to extract names from CSV if available
                    pass
                emails_to_send.append(email_data)
            
            # Start sending
            result = self.email_sender.send_bulk_emails(
                emails_to_send, subject, body, progress_callback=self.update_email_progress
            )
            
            if result['status'] == 'started':
                self.send_to_valid_btn.config(state=tk.DISABLED)
                self.send_to_valid_risky_btn.config(state=tk.DISABLED)
                self.cancel_email_btn.config(state=tk.NORMAL)
                self.email_progress_label.config(text=f"Started sending to {len(target_emails)} emails")
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start email campaign: {str(e)}")
    
    def update_email_progress(self, progress, current, total, result):
        """Update email sending progress"""
        self.email_progress_var.set(progress)
        
        if result['status'] == 'completed':
            self.email_progress_label.config(text=f"Completed! Sent {current} emails")
            self.send_to_valid_btn.config(state=tk.NORMAL)
            self.send_to_valid_risky_btn.config(state=tk.NORMAL)
            self.cancel_email_btn.config(state=tk.DISABLED)
            
            # Show completion stats
            stats = self.email_sender.get_campaign_stats()
            messagebox.showinfo("Campaign Complete", 
                              f"Email campaign completed!\n\n"
                              f"Total sent: {stats['total_sent']}\n"
                              f"Successful: {stats['successful']}\n"
                              f"Failed: {stats['failed']}\n"
                              f"Duration: {stats.get('duration', 0):.1f} seconds")
        else:
            self.email_progress_label.config(text=f"Sending {current}/{total} emails...")
    
    def cancel_email_sending(self):
        """Cancel ongoing email campaign"""
        if hasattr(self, 'email_sender'):
            self.email_sender.cancel_sending()
            self.email_progress_label.config(text="Sending cancelled")
            self.send_to_valid_btn.config(state=tk.NORMAL)
            self.send_to_valid_risky_btn.config(state=tk.NORMAL)
            self.cancel_email_btn.config(state=tk.DISABLED)
            self.email_progress_var.set(0)
        
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
        
        # Enable email sender buttons if there are valid emails
        if valid_count > 0:
            self.send_to_valid_btn.config(state=tk.NORMAL)
        if valid_count > 0 or risky_count > 0:
            self.send_to_valid_risky_btn.config(state=tk.NORMAL)
        
        # Update email sender tab status
        if hasattr(self, 'email_sender_status_label'):
            if valid_count > 0:
                self.email_sender_status_label.config(
                    text=f"✅ {valid_count} valid emails ready to send! {risky_count} risky emails also available.", 
                    foreground='green'
                )
            elif risky_count > 0:
                self.email_sender_status_label.config(
                    text=f"⚠️ {risky_count} risky emails available (no valid emails found)", 
                    foreground='orange'
                )
            else:
                self.email_sender_status_label.config(
                    text="❌ No valid or risky emails found", 
                    foreground='red'
                )
        
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
        
        # Reset email sender buttons
        if hasattr(self, 'send_to_valid_btn'):
            self.send_to_valid_btn.config(state=tk.DISABLED)
        if hasattr(self, 'email_sender_status_label'):
            self.email_sender_status_label.config(
                text="⚠️ Please verify emails first in the Email Verification tab",
                foreground='orange'
            )
    
    def setup_ai_creator_tab(self):
        """Setup the AI Message Creator tab"""
        # Configure grid weights for AI creator tab
        self.ai_creator_tab.columnconfigure(0, weight=1)
        
        # AI Configuration and Settings section (side by side)
        config_settings_frame = ttk.Frame(self.ai_creator_tab)
        config_settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        config_settings_frame.columnconfigure(0, weight=1)
        config_settings_frame.columnconfigure(1, weight=1)
        
        # AI Configuration section (left side)
        config_frame = ttk.LabelFrame(config_settings_frame, text="AI Configuration", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Provider selection
        provider_frame = ttk.Frame(config_frame)
        provider_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(provider_frame, text="AI Provider:").pack(side=tk.LEFT)
        self.ai_provider_var = tk.StringVar(value="openai")
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.ai_provider_var, 
                                     values=["openai", "anthropic", "google", "local"], 
                                     state="readonly", width=15)
        provider_combo.pack(side=tk.LEFT, padx=(10, 0))
        provider_combo.bind('<<ComboboxSelected>>', self.on_ai_provider_change)
        
        # API Key input
        api_frame = ttk.Frame(config_frame)
        api_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT)
        self.ai_api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(api_frame, textvariable=self.ai_api_key_var, width=30, show="*")
        api_key_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Test connection button
        test_ai_frame = ttk.Frame(config_frame)
        test_ai_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(test_ai_frame, text="Test AI Connection", 
                  command=self.test_ai_connection).pack(side=tk.LEFT)
        self.ai_connection_status = ttk.Label(test_ai_frame, text="", foreground='black')
        self.ai_connection_status.pack(side=tk.LEFT, padx=(20, 0))
        
        # AI Settings section (right side)
        settings_frame = ttk.LabelFrame(config_settings_frame, text="AI Settings", padding="10")
        settings_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Row 1: Model and Temperature
        ttk.Label(settings_frame, text="Model:").grid(row=0, column=0, sticky=tk.W)
        self.ai_model_var = tk.StringVar(value="gpt-4")
        model_combo = ttk.Combobox(settings_frame, textvariable=self.ai_model_var, 
                                  values=["gpt-4", "gpt-3.5-turbo"], state="readonly", width=15)
        model_combo.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(settings_frame, text="Temperature:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.ai_temperature_var = tk.DoubleVar(value=0.7)
        temp_scale = ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=self.ai_temperature_var, 
                              orient=tk.HORIZONTAL, length=80)
        temp_scale.grid(row=0, column=3, padx=(10, 0))
        
        # Row 2: Tone and Length
        ttk.Label(settings_frame, text="Tone:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.ai_tone_var = tk.StringVar(value="professional")
        tone_combo = ttk.Combobox(settings_frame, textvariable=self.ai_tone_var, 
                                 values=["professional", "casual", "friendly", "urgent", "persuasive"], 
                                 state="readonly", width=15)
        tone_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(settings_frame, text="Length:").grid(row=1, column=2, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.ai_length_var = tk.StringVar(value="medium")
        length_combo = ttk.Combobox(settings_frame, textvariable=self.ai_length_var, 
                                   values=["short", "medium", "long"], state="readonly", width=15)
        length_combo.grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        
        # Row 3: Industry and Target Audience
        ttk.Label(settings_frame, text="Industry:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.ai_industry_var = tk.StringVar(value="general")
        industry_combo = ttk.Combobox(settings_frame, textvariable=self.ai_industry_var, 
                                     values=["general", "ecommerce", "b2b", "saas", "education", "healthcare"], 
                                     state="readonly", width=15)
        industry_combo.grid(row=2, column=1, padx=(10, 0), pady=(10, 0))
        
        ttk.Label(settings_frame, text="Target:").grid(row=2, column=2, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        self.ai_target_var = tk.StringVar(value="customers")
        target_combo = ttk.Combobox(settings_frame, textvariable=self.ai_target_var, 
                                   values=["customers", "prospects", "employees", "partners"], 
                                   state="readonly", width=15)
        target_combo.grid(row=2, column=3, padx=(10, 0), pady=(10, 0))
        
        # Quick Templates section
        templates_frame = ttk.LabelFrame(self.ai_creator_tab, text="Quick Templates", padding="10")
        templates_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Template buttons in a grid
        template_buttons = [
            ("Welcome", "welcome"), ("Follow-up", "follow_up"), ("Product Launch", "product_launch"),
            ("Abandoned Cart", "abandoned_cart"), ("Newsletter", "newsletter"), ("Promotion", "promotion")
        ]
        
        for i, (label, template_key) in enumerate(template_buttons):
            row = i // 3
            col = i % 3
            btn = ttk.Button(templates_frame, text=label, 
                           command=lambda t=template_key: self.load_template(t))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Configure template frame columns
        for i in range(3):
            templates_frame.columnconfigure(i, weight=1)
        
        # Prompt Input section
        prompt_frame = ttk.LabelFrame(self.ai_creator_tab, text="Email Description", padding="10")
        prompt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(prompt_frame, text="Describe the email you want to create:").grid(row=0, column=0, sticky=tk.W)
        
        self.prompt_text = tk.Text(prompt_frame, height=4, width=70)
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Generate button
        generate_frame = ttk.Frame(prompt_frame)
        generate_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.generate_btn = ttk.Button(generate_frame, text="Generate Email", 
                                     command=self.generate_ai_email, style='Accent.TButton')
        self.generate_btn.pack(side=tk.LEFT)
        
        self.ai_progress_label = ttk.Label(generate_frame, text="Ready to generate")
        self.ai_progress_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Generated Content section
        content_frame = ttk.LabelFrame(self.ai_creator_tab, text="Generated Email", padding="10")
        content_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Subject
        ttk.Label(content_frame, text="Subject:").grid(row=0, column=0, sticky=tk.W)
        self.ai_subject_var = tk.StringVar()
        subject_entry = ttk.Entry(content_frame, textvariable=self.ai_subject_var, width=60)
        subject_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Body
        ttk.Label(content_frame, text="Body:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.ai_body_text = tk.Text(content_frame, height=8, width=60)
        self.ai_body_text.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=(10, 0))
        
        # Scrollbar for body text
        body_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.ai_body_text.yview)
        self.ai_body_text.configure(yscrollcommand=body_scrollbar.set)
        body_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S), pady=(10, 0))
        
        # Action buttons
        action_frame = ttk.Frame(self.ai_creator_tab)
        action_frame.grid(row=4, column=0, pady=(0, 20))
        
        self.send_to_campaign_btn = ttk.Button(action_frame, text="Send to Campaign Commander", 
                                             command=self.send_to_campaign_commander, state=tk.DISABLED)
        self.send_to_campaign_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refine_btn = ttk.Button(action_frame, text="Refine Content", 
                                   command=self.refine_ai_content, state=tk.DISABLED)
        self.refine_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(action_frame, text="Clear", 
                                  command=self.clear_ai_content)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Status section
        status_frame = ttk.Frame(self.ai_creator_tab)
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.ai_status_label = ttk.Label(status_frame, text="Ready to create AI-powered emails", 
                                       foreground='blue', font=('Arial', 9))
        self.ai_status_label.pack(side=tk.LEFT)
        
        # Initialize AI creator
        self.ai_creator = None
        self.current_ai_result = None
    
    def on_ai_provider_change(self, event):
        """Handle AI provider change"""
        provider = self.ai_provider_var.get()
        
        # Update model options based on provider
        if provider == "openai":
            models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
            self.ai_model_var.set("gpt-4")
        elif provider == "anthropic":
            models = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            self.ai_model_var.set("claude-3-sonnet")
        elif provider == "google":
            models = ["gemini-pro", "gemini-pro-vision"]
            self.ai_model_var.set("gemini-pro")
        elif provider == "local":
            models = ["llama2", "mistral", "codellama"]
            self.ai_model_var.set("llama2")
        
        # Update model combo values
        model_combo = self.ai_creator_tab.winfo_children()[1].winfo_children()[1].winfo_children()[1]
        model_combo['values'] = models
        
        # Clear API key and status
        self.ai_api_key_var.set("")
        self.ai_connection_status.config(text="", foreground='black')
        self.ai_status_label.config(text=f"Provider changed to {provider}. Please enter API key and test connection.")
    
    def test_ai_connection(self):
        """Test the AI connection settings"""
        provider = self.ai_provider_var.get()
        api_key = self.ai_api_key_var.get()
        
        if not api_key:
            self.ai_connection_status.config(text="Please enter API key", foreground='red')
            return
        
        try:
            # Create AI creator instance
            config = {
                'model': self.ai_model_var.get(),
                'temperature': self.ai_temperature_var.get()
            }
            
            self.ai_creator = AIMessageCreator(provider, api_key, config)
            result = self.ai_creator.test_connection()
            
            if result['status'] == 'success':
                self.ai_connection_status.config(text=result['message'], foreground='green')
                self.ai_status_label.config(text=f"✅ Connected to {result['provider']} using {result['model']}")
            else:
                self.ai_connection_status.config(text=result['message'], foreground='red')
                self.ai_status_label.config(text="❌ Connection failed")
                
        except Exception as e:
            self.ai_connection_status.config(text=f"Connection error: {str(e)}", foreground='red')
            self.ai_status_label.config(text="❌ Connection error")
    
    def load_template(self, template_key):
        """Load a predefined email template"""
        if template_key in EMAIL_TEMPLATES:
            template = EMAIL_TEMPLATES[template_key]
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", template['prompt'])
            
            # Set template-specific settings
            self.ai_tone_var.set(template['tone'])
            self.ai_length_var.set(template['length'])
            
            self.ai_status_label.config(text=f"Loaded {template['name']} template")
    
    def generate_ai_email(self):
        """Generate email content using AI"""
        if not self.ai_creator:
            messagebox.showerror("Error", "Please test AI connection first")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a description of the email you want to create")
            return
        
        # Update UI
        self.generate_btn.config(state=tk.DISABLED)
        self.ai_progress_label.config(text="Generating email...")
        self.ai_status_label.config(text="🤖 AI is creating your email...")
        
        # Get AI settings
        tone = self.ai_tone_var.get()
        length = self.ai_length_var.get()
        industry = self.ai_industry_var.get()
        target_audience = self.ai_target_var.get()
        
        try:
            # Generate email in separate thread
            import threading
            self.ai_generation_thread = threading.Thread(
                target=self._generate_ai_email_worker,
                args=(prompt, tone, length, industry, target_audience)
            )
            self.ai_generation_thread.daemon = True
            self.ai_generation_thread.start()
            
        except Exception as e:
            self.ai_progress_label.config(text="Generation failed")
            self.ai_status_label.config(text=f"❌ Error: {str(e)}")
            self.generate_btn.config(state=tk.NORMAL)
    
    def _generate_ai_email_worker(self, prompt, tone, length, industry, target_audience):
        """Worker thread for AI email generation"""
        try:
            result = self.ai_creator.generate_email(prompt, tone, length, industry, target_audience)
            
            # Update UI in main thread
            self.root.after(0, self._ai_generation_completed, result)
            
        except Exception as e:
            self.root.after(0, self._ai_generation_error, str(e))
    
    def _ai_generation_completed(self, result):
        """Handle AI generation completion"""
        self.generate_btn.config(state=tk.NORMAL)
        
        if result['status'] == 'success':
            # Update UI with generated content
            self.ai_subject_var.set(result['subject'])
            self.ai_body_text.delete("1.0", tk.END)
            self.ai_body_text.insert("1.0", result['body'])
            
            # Store result for later use
            self.current_ai_result = result
            
            # Enable action buttons
            self.send_to_campaign_btn.config(state=tk.NORMAL)
            self.refine_btn.config(state=tk.NORMAL)
            
            # Update status
            cost_info = f" (Cost: ${result.get('estimated_cost', 0):.4f})" if result.get('estimated_cost', 0) > 0 else ""
            self.ai_progress_label.config(text="Generation completed!")
            self.ai_status_label.config(
                text=f"✅ Email generated using {result['provider']} ({result['model']}){cost_info}",
                foreground='green'
            )
            
            # Show suggestions if any
            if result.get('suggestions'):
                suggestions_text = "\n".join([f"• {s}" for s in result['suggestions']])
                messagebox.showinfo("AI Suggestions", f"Suggestions for improvement:\n\n{suggestions_text}")
                
        else:
            self.ai_progress_label.config(text="Generation failed")
            self.ai_status_label.config(text=f"❌ {result.get('message', 'Unknown error')}", foreground='red')
    
    def _ai_generation_error(self, error_message):
        """Handle AI generation error"""
        self.generate_btn.config(state=tk.NORMAL)
        self.ai_progress_label.config(text="Generation failed")
        self.ai_status_label.config(text=f"❌ Error: {error_message}", foreground='red')
    
    def send_to_campaign_commander(self):
        """Send generated content to Campaign Commander tab"""
        if not self.current_ai_result:
            return
        
        # Switch to Campaign Commander tab
        self.notebook.select(2)  # Index 2 is Campaign Commander tab
        
        # Update Campaign Commander fields
        if hasattr(self, 'subject_var'):
            self.subject_var.set(self.ai_subject_var.get())
        
        if hasattr(self, 'body_text'):
            self.body_text.delete("1.0", tk.END)
            self.body_text.insert("1.0", self.ai_body_text.get("1.0", tk.END))
        
        # Update status
        self.ai_status_label.config(text="✅ Content sent to Campaign Commander tab", foreground='green')
        
        # Show confirmation
        messagebox.showinfo("Content Sent", 
                          "Email content has been sent to the Campaign Commander tab.\n"
                          "You can now configure your SMTP settings and send the campaign!")
    
    def refine_ai_content(self):
        """Refine the generated content using AI"""
        if not self.current_ai_result or not self.ai_creator:
            return
        
        # Create refinement prompt
        current_subject = self.ai_subject_var.get()
        current_body = self.ai_body_text.get("1.0", tk.END).strip()
        
        refinement_prompt = f"""
Please improve the following email content:

Current Subject: {current_subject}
Current Body: {current_body}

Please make the following improvements:
1. Make the subject line more compelling and click-worthy
2. Improve the email body to be more engaging and persuasive
3. Ensure there's a clear call-to-action
4. Make the tone more {self.ai_tone_var.get()}
5. Optimize for {self.ai_length_var.get()} length

Please provide the improved version in the same format as before.
"""
        
        # Update UI
        self.ai_progress_label.config(text="Refining content...")
        self.ai_status_label.config(text="🤖 AI is refining your email...")
        
        try:
            # Refine content in separate thread
            import threading
            self.ai_refinement_thread = threading.Thread(
                target=self._refine_ai_content_worker,
                args=(refinement_prompt,)
            )
            self.ai_refinement_thread.daemon = True
            self.ai_refinement_thread.start()
            
        except Exception as e:
            self.ai_progress_label.config(text="Refinement failed")
            self.ai_status_label.config(text=f"❌ Error: {str(e)}")
    
    def _refine_ai_content_worker(self, refinement_prompt):
        """Worker thread for AI content refinement"""
        try:
            result = self.ai_creator.generate_email(
                refinement_prompt, 
                self.ai_tone_var.get(), 
                self.ai_length_var.get(), 
                self.ai_industry_var.get(), 
                self.ai_target_var.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self._ai_refinement_completed, result)
            
        except Exception as e:
            self.root.after(0, self._ai_refinement_error, str(e))
    
    def _ai_refinement_completed(self, result):
        """Handle AI refinement completion"""
        if result['status'] == 'success':
            # Update UI with refined content
            self.ai_subject_var.set(result['subject'])
            self.ai_body_text.delete("1.0", tk.END)
            self.ai_body_text.insert("1.0", result['body'])
            
            # Update stored result
            self.current_ai_result = result
            
            # Update status
            cost_info = f" (Cost: ${result.get('estimated_cost', 0):.4f})" if result.get('estimated_cost', 0) > 0 else ""
            self.ai_progress_label.config(text="Refinement completed!")
            self.ai_status_label.config(
                text=f"✅ Email refined using {result['provider']} ({result['model']}){cost_info}",
                foreground='green'
            )
        else:
            self.ai_progress_label.config(text="Refinement failed")
            self.ai_status_label.config(text=f"❌ {result.get('message', 'Unknown error')}", foreground='red')
    
    def _ai_refinement_error(self, error_message):
        """Handle AI refinement error"""
        self.ai_progress_label.config(text="Refinement failed")
        self.ai_status_label.config(text=f"❌ Error: {error_message}", foreground='red')
    
    def clear_ai_content(self):
        """Clear all AI-generated content"""
        self.ai_subject_var.set("")
        self.ai_body_text.delete("1.0", tk.END)
        self.prompt_text.delete("1.0", tk.END)
        
        # Reset buttons
        self.send_to_campaign_btn.config(state=tk.DISABLED)
        self.refine_btn.config(state=tk.DISABLED)
        
        # Clear stored result
        self.current_ai_result = None
        
        # Reset status
        self.ai_progress_label.config(text="Ready to generate")
        self.ai_status_label.config(text="Ready to create AI-powered emails", foreground='blue')
    
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
    app = MailCommanderProApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
