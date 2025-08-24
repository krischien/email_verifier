import re
import socket
import smtplib
import dns.resolver
from email_validator import validate_email, EmailNotValidError
import pandas as pd
from typing import Dict, List, Tuple
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailVerifier:
    def __init__(self, max_workers=20, fast_mode=True, timeout=5):
        self.max_workers = max_workers
        self.fast_mode = fast_mode
        self.timeout = timeout
        self.cancelled = False
        self.progress = 0
        self.total_emails = 0
        
    def check_email_format(self, email: str) -> bool:
        """Check if email has valid syntax"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def check_mx_record(self, domain: str) -> bool:
        """Check if domain has valid MX records - optimized for speed"""
        try:
            # Use faster timeout for DNS resolution
            resolver = dns.resolver.Resolver()
            resolver.timeout = 2.0  # 2 seconds timeout
            resolver.lifetime = 3.0  # 3 seconds total lifetime
            
            mx_records = resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except Exception as e:
            logger.debug(f"MX check failed for {domain}: {e}")
            return False
    
    def check_smtp_connection_fast(self, email: str) -> str:
        """Fast SMTP check with minimal timeout"""
        try:
            domain = email.split('@')[1]
            
            # Get MX records with fast timeout
            resolver = dns.resolver.Resolver()
            resolver.timeout = 1.0
            resolver.lifetime = 2.0
            
            try:
                mx_records = resolver.resolve(domain, 'MX')
                if not mx_records:
                    return "invalid"
            except:
                return "invalid"
            
            # Sort by priority and try only the first MX server
            mx_records = sorted(mx_records, key=lambda x: x.preference)
            mx_record = mx_records[0]  # Only try the first one for speed
            
            try:
                # Very fast SMTP check
                server = smtplib.SMTP(str(mx_record.exchange), timeout=self.timeout)
                
                # Quick connection test without full handshake
                server.helo('test.com')
                
                # Try RCPT command directly (faster than full email)
                code, message = server.rcpt(email)
                server.quit()
                
                if code == 250:
                    return "valid"
                elif code == 550:
                    return "invalid"
                else:
                    return "risky"
                    
            except smtplib.SMTPRecipientsRefused:
                return "invalid"
            except smtplib.SMTPResponseException as e:
                if e.smtp_code == 550:
                    return "invalid"
                else:
                    return "risky"
            except Exception:
                return "risky"
            
        except Exception as e:
            logger.debug(f"Fast SMTP check failed for {email}: {e}")
            return "risky"
    
    def check_smtp_connection_standard(self, email: str) -> str:
        """Standard SMTP check with full validation"""
        try:
            domain = email.split('@')[1]
            
            # Get MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return "invalid"
            
            # Sort by priority
            mx_records = sorted(mx_records, key=lambda x: x.preference)
            
            for mx_record in mx_records[:2]:  # Try first 2 MX servers
                try:
                    server = smtplib.SMTP(str(mx_record.exchange), timeout=10)
                    server.starttls()
                    
                    # Try to send a test email
                    server.helo('test.com')
                    server.mail('test@test.com')
                    code, message = server.rcpt(email)
                    server.quit()
                    
                    if code == 250:
                        return "valid"
                    elif code == 550:
                        return "invalid"
                    else:
                        return "risky"
                        
                except smtplib.SMTPRecipientsRefused:
                    return "invalid"
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 550:
                        return "invalid"
                    else:
                        return "risky"
                except Exception:
                    continue
            
            return "risky"
            
        except Exception as e:
            logger.debug(f"Standard SMTP check failed for {email}: {e}")
            return "risky"
    
    def verify_single_email(self, email: str) -> Dict[str, str]:
        """Verify a single email address"""
        if self.cancelled:
            return {"email": email, "status": "cancelled", "format": False, "mx": False, "ping": "cancelled"}
        
        result = {
            "email": email,
            "format": False,
            "mx": False,
            "ping": "invalid",
            "status": "invalid"
        }
        
        # Step 1: Check format (very fast)
        result["format"] = self.check_email_format(email)
        if not result["format"]:
            result["status"] = "invalid"
            return result
        
        # Step 2: Check MX record (fast)
        domain = email.split('@')[1]
        result["mx"] = self.check_mx_record(domain)
        if not result["mx"]:
            result["status"] = "invalid"
            return result
        
        # Step 3: Check SMTP connection (choose method based on mode)
        if self.fast_mode:
            result["ping"] = self.check_smtp_connection_fast(email)
        else:
            result["ping"] = self.check_smtp_connection_standard(email)
        
        result["status"] = result["ping"]
        
        return result
    
    def verify_emails_batch(self, emails: List[str], progress_callback=None) -> List[Dict[str, str]]:
        """Verify a batch of emails with progress tracking"""
        self.total_emails = len(emails)
        self.progress = 0
        self.cancelled = False
        results = []
        
        # Optimize worker count for better performance
        optimal_workers = min(self.max_workers, len(emails), 50)
        
        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            future_to_email = {executor.submit(self.verify_single_email, email): email for email in emails}
            
            for future in as_completed(future_to_email):
                if self.cancelled:
                    # Cancel remaining futures
                    for f in future_to_email:
                        f.cancel()
                    break
                
                try:
                    result = future.result()
                    results.append(result)
                    self.progress += 1
                    
                    if progress_callback:
                        progress_callback(self.progress, self.total_emails)
                        
                except Exception as e:
                    logger.error(f"Error processing email: {e}")
                    results.append({
                        "email": future_to_email[future],
                        "status": "error",
                        "format": False,
                        "mx": False,
                        "ping": "error"
                    })
        
        return results
    
    def cancel_verification(self):
        """Cancel the current verification process"""
        self.cancelled = True
    
    def get_progress(self) -> Tuple[int, int]:
        """Get current progress"""
        return self.progress, self.total_emails
    
    def generate_csv_links(self, results: List[Dict[str, str]]) -> Dict[str, str]:
        """Generate CSV files and return download links"""
        df = pd.DataFrame(results)
        
        # Create different CSV files
        all_emails = df.to_csv(index=False)
        valid_emails = df[df['status'] == 'valid'].to_csv(index=False)
        risky_emails = df[df['status'] == 'risky'].to_csv(index=False)
        valid_and_risky = df[df['status'].isin(['valid', 'risky'])].to_csv(index=False)
        
        # In a real app, you'd save these to files and generate actual download links
        # For now, we'll return the CSV content as strings
        return {
            "all_leads": all_emails,
            "valid_only": valid_emails,
            "risky_only": risky_emails,
            "valid_and_risky": valid_and_risky
        }
