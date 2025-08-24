import pandas as pd
import os
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CSVProcessor:
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    def detect_email_column(self, df: pd.DataFrame) -> Optional[str]:
        """Automatically detect the email column in the dataframe"""
        email_columns = []
        
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['email', 'e-mail', 'mail', 'email_address']):
                email_columns.append(col)
        
        if email_columns:
            return email_columns[0]  # Return the first matching column
        
        # If no obvious email column found, try to detect by content
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                # Check if most values contain @ symbol
                sample_values = df[col].dropna().head(100)
                if len(sample_values) > 0:
                    email_like = sample_values.astype(str).str.contains('@').sum()
                    if email_like / len(sample_values) > 0.8:  # 80% contain @
                        return col
        
        return None
    
    def read_csv_file(self, file_path: str) -> Tuple[pd.DataFrame, Optional[str]]:
        """Read CSV file and detect email column"""
        try:
            # Determine file format
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Detect email column
            email_column = self.detect_email_column(df)
            
            if email_column is None:
                raise ValueError("No email column detected in the file")
            
            return df, email_column
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def extract_emails(self, df: pd.DataFrame, email_column: str) -> List[str]:
        """Extract emails from the specified column"""
        try:
            emails = df[email_column].dropna().astype(str).tolist()
            
            # Basic cleaning
            cleaned_emails = []
            for email in emails:
                email = email.strip()
                if email and '@' in email:
                    cleaned_emails.append(email)
            
            return cleaned_emails
            
        except Exception as e:
            logger.error(f"Error extracting emails: {e}")
            raise
    
    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate if the file can be processed"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            return False, f"Unsupported file format. Supported formats: {', '.join(self.supported_formats)}"
        
        try:
            # Try to read the file
            df, email_column = self.read_csv_file(file_path)
            if email_column is None:
                return False, "No email column detected"
            
            emails = self.extract_emails(df, email_column)
            if len(emails) == 0:
                return False, "No valid emails found in the file"
            
            return True, f"File is valid. Found {len(emails)} emails in column '{email_column}'"
            
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    def get_file_info(self, file_path: str) -> dict:
        """Get information about the file"""
        try:
            df, email_column = self.read_csv_file(file_path)
            emails = self.extract_emails(df, email_column)
            
            return {
                "total_rows": len(df),
                "email_column": email_column,
                "total_emails": len(emails),
                "file_size": os.path.getsize(file_path),
                "file_format": os.path.splitext(file_path)[1].lower()
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {}
