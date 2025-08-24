import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import threading
from typing import List, Dict, Optional
import logging

class EmailSender:
    """Configurable email sender for burst campaigns"""
    
    def __init__(self, config: Dict):
        """
        Initialize email sender with configuration
        
        Args:
            config: Dictionary containing email settings
                - smtp_server: SMTP server address
                - smtp_port: SMTP port (usually 587 or 465)
                - username: Email username/address
                - password: Email password or app password
                - use_tls: Whether to use TLS (default True)
                - use_ssl: Whether to use SSL (default False)
                - rate_limit: Emails per minute (default 60)
                - delay_between: Delay between emails in seconds (default 1)
        """
        self.config = config
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.use_tls = config.get('use_tls', True)
        self.use_ssl = config.get('use_ssl', False)
        self.rate_limit = config.get('rate_limit', 60)  # emails per minute
        self.delay_between = config.get('delay_between', 1)  # seconds between emails
        
        # Campaign tracking
        self.campaign_stats = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Threading control
        self.is_sending = False
        self.cancelled = False
        self.current_thread = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self) -> Dict[str, str]:
        """Test SMTP connection with current settings"""
        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.username, self.password)
            server.quit()
            
            return {
                'status': 'success',
                'message': f'Connection successful to {self.smtp_server}:{self.smtp_port}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            }
    
    def send_single_email(self, to_email: str, subject: str, body: str, 
                         html_body: str = None, attachments: List[str] = None) -> Dict[str, str]:
        """Send a single email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                    except Exception as e:
                        self.logger.warning(f"Failed to attach {file_path}: {e}")
            
            # Send email
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            return {
                'status': 'success',
                'message': f'Email sent successfully to {to_email}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to send email to {to_email}: {str(e)}'
            }
    
    def send_bulk_emails(self, emails: List[Dict], subject: str, body: str,
                         html_body: str = None, attachments: List[str] = None,
                         progress_callback=None) -> Dict[str, any]:
        """
        Send bulk emails with rate limiting and progress tracking
        
        Args:
            emails: List of dictionaries with 'email' key and optional 'name' key
            subject: Email subject (can use {name} placeholder)
            body: Email body (can use {name} placeholder)
            html_body: HTML email body (can use {name} placeholder)
            attachments: List of file paths to attach
            progress_callback: Function to call with progress updates
        
        Returns:
            Dictionary with campaign results and statistics
        """
        if self.is_sending:
            return {'status': 'error', 'message': 'Already sending emails'}
        
        self.is_sending = True
        self.cancelled = False
        self.campaign_stats = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        # Start sending in background thread
        self.current_thread = threading.Thread(
            target=self._send_bulk_emails_worker,
            args=(emails, subject, body, html_body, attachments, progress_callback)
        )
        self.current_thread.start()
        
        return {
            'status': 'started',
            'message': f'Started sending {len(emails)} emails',
            'campaign_id': int(time.time())
        }
    
    def _send_bulk_emails_worker(self, emails: List[Dict], subject: str, body: str,
                                 html_body: str = None, attachments: List[str] = None,
                                 progress_callback=None):
        """Worker thread for sending bulk emails"""
        results = []
        
        try:
            for i, email_data in enumerate(emails):
                if self.cancelled:
                    break
                
                to_email = email_data.get('email', '')
                name = email_data.get('name', '')
                
                # Personalize content
                personalized_subject = subject.replace('{name}', name) if name else subject
                personalized_body = body.replace('{name}', name) if name else body
                personalized_html = html_body.replace('{name}', name) if html_body and name else html_body
                
                # Send email
                result = self.send_single_email(
                    to_email, personalized_subject, personalized_body, 
                    personalized_html, attachments
                )
                
                # Update statistics
                self.campaign_stats['total_sent'] += 1
                if result['status'] == 'success':
                    self.campaign_stats['successful'] += 1
                else:
                    self.campaign_stats['failed'] += 1
                
                # Store result
                results.append({
                    'email': to_email,
                    'name': name,
                    'status': result['status'],
                    'message': result['message'],
                    'timestamp': time.time()
                })
                
                # Progress callback
                if progress_callback:
                    progress = (i + 1) / len(emails) * 100
                    progress_callback(progress, i + 1, len(emails), result)
                
                # Rate limiting
                if i < len(emails) - 1:  # Don't delay after last email
                    time.sleep(self.delay_between)
        
        except Exception as e:
            self.logger.error(f"Error in bulk email worker: {e}")
        
        finally:
            self.campaign_stats['end_time'] = time.time()
            self.is_sending = False
            
            if progress_callback:
                progress_callback(100, len(emails), len(emails), {'status': 'completed'})
    
    def cancel_sending(self):
        """Cancel ongoing email campaign"""
        self.cancelled = True
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=5)
        self.is_sending = False
    
    def get_campaign_stats(self) -> Dict:
        """Get current campaign statistics"""
        stats = self.campaign_stats.copy()
        if stats['start_time'] and stats['end_time']:
            stats['duration'] = stats['end_time'] - stats['start_time']
        elif stats['start_time']:
            stats['duration'] = time.time() - stats['start_time']
        return stats
    
    def get_status(self) -> Dict:
        """Get current sender status"""
        return {
            'is_sending': self.is_sending,
            'cancelled': self.cancelled,
            'campaign_stats': self.get_campaign_stats(),
            'config': {
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'username': self.username,
                'rate_limit': self.rate_limit,
                'delay_between': self.delay_between
            }
        }


# Predefined configurations for common email providers
EMAIL_PROVIDERS = {
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False,
        'rate_limit': 60,
        'delay_between': 1
    },
    'gmail_ssl': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 465,
        'use_tls': False,
        'use_ssl': True,
        'rate_limit': 60,
        'delay_between': 1
    },
    'outlook': {
        'smtp_server': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False,
        'rate_limit': 60,
        'delay_between': 1
    },
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False,
        'rate_limit': 60,
        'delay_between': 1
    },
    'custom': {
        'smtp_server': '',
        'smtp_port': 587,
        'use_tls': True,
        'use_ssl': False,
        'rate_limit': 60,
        'delay_between': 1
    }
}
