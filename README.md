# Email Verifier Pro

A comprehensive Python application for verifying email addresses from CSV/Excel files with a modern GUI interface and command-line support.

## Features

- **Email Format Validation**: Checks email syntax using RFC standards
- **MX Record Verification**: Validates domain MX records
- **SMTP Connection Testing**: Tests actual email server connectivity
- **Progress Tracking**: Real-time progress bar with cancellation support
- **Multiple Output Formats**: Generate separate CSV files for different result categories
- **Modern GUI**: User-friendly interface built with tkinter
- **Command-Line Interface**: CLI version for batch processing and automation
- **Multi-threaded Processing**: Configurable concurrent workers for faster processing

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   python -c "import pandas, dns.resolver, email_validator; print('All dependencies installed successfully!')"
   ```

## Usage

### GUI Application

1. **Run the main application**:
   ```bash
   python main_app.py
   ```

2. **Select your CSV/Excel file**:
   - Click "Browse" to select a file
   - Supported formats: `.csv`, `.xlsx`, `.xls`
   - The app will automatically detect email columns

3. **Configure settings**:
   - Adjust the number of concurrent workers (default: 10)
   - Higher worker count = faster processing but more resource usage

4. **Start verification**:
   - Click "Start Verification"
   - Monitor progress in real-time
   - Cancel anytime with the "Cancel" button

5. **Download results**:
   - All Leads: Complete results
   - Valid Only: Emails marked as valid
   - Risky Only: Emails marked as risky
   - Valid + Risky: Combination of valid and risky emails

### Command-Line Interface

For batch processing or automation:

```bash
# Basic usage
python cli_version.py sample_emails.csv

# With custom output directory
python cli_version.py sample_emails.csv -o ./my_results

# With custom worker count
python cli_version.py sample_emails.csv -w 20

# Help
python cli_version.py --help
```

## Verification Process

The application performs a three-step verification process:

### 1. Format Check (Syntax)
- Validates email format according to RFC standards
- Checks for proper structure (local@domain)
- Uses the `email-validator` library

### 2. MX Record Check
- Queries DNS for MX records
- Verifies domain can receive emails
- Uses `dns.resolver` for reliable DNS lookups

### 3. SMTP Connection Test (Ping)
- Attempts SMTP connection to mail servers
- Tests actual email delivery capability
- Categorizes results:
  - **Valid**: Email accepts messages (SMTP 250)
  - **Risky**: Email server responds but with warnings/restrictions
  - **Invalid**: Email rejected (SMTP 550) or connection failed

## Result Categories

- **Valid**: Passes all three checks, safe to use
- **Risky**: Passes format and MX but SMTP behavior is uncertain
- **Invalid**: Fails one or more checks, avoid using

## File Format Support

### Input Files
- **CSV**: Comma-separated values
- **Excel**: `.xlsx` and `.xls` formats
- **Auto-detection**: Automatically finds email columns

### Output Files
- **CSV format** with columns:
  - `email`: Original email address
  - `format`: Format validation result (True/False)
  - `mx`: MX record check result (True/False)
  - `ping`: SMTP test result (valid/risky/invalid)
  - `status`: Final verification status

## Performance Tips

1. **Worker Count**: 
   - Start with 10 workers
   - Increase for faster processing (if your system can handle it)
   - Too many workers may trigger rate limiting

2. **File Size**:
   - Large files (>10,000 emails) may take significant time
   - Use CLI version for very large datasets
   - Consider processing in batches

3. **Network**:
   - Faster internet = faster verification
   - Some email servers may be slow to respond

## Troubleshooting

### Common Issues

1. **"No email column detected"**
   - Ensure your CSV has a column with email addresses
   - Column names like "email", "e-mail", "mail" are auto-detected
   - Check that emails contain @ symbols

2. **"MX check failed"**
   - Domain may not have mail servers
   - DNS resolution issues
   - Check internet connection

3. **"SMTP connection timeout"**
   - Mail server may be slow
   - Firewall blocking connections
   - Increase timeout settings if needed

4. **Slow performance**
   - Reduce worker count
   - Check internet speed
   - Some email providers are slower than others

### Error Handling

The application gracefully handles:
- Network timeouts
- DNS resolution failures
- Invalid email formats
- File reading errors
- Memory issues with large files

## Development

### Project Structure

```
email_verifier/
├── email_verifier.py      # Core verification logic
├── csv_processor.py       # CSV/Excel file handling
├── main_app.py           # GUI application
├── cli_version.py        # Command-line interface
├── requirements.txt      # Python dependencies
├── sample_emails.csv     # Test data
└── README.md            # This file
```

### Extending the Application

- **Add new verification methods**: Extend `EmailVerifier` class
- **Support new file formats**: Modify `CSVProcessor` class
- **Custom output formats**: Modify `generate_csv_links` method
- **Additional UI features**: Extend `EmailVerifierApp` class

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the application
3. Test with the provided sample file
4. Ensure all dependencies are properly installed

## Sample Usage

```python
# Quick test with sample file
python cli_version.py sample_emails.csv

# GUI application
python main_app.py

# Verify specific file with custom settings
python cli_version.py my_emails.csv -w 15 -o ./verification_results
```

## Performance Benchmarks

Typical processing speeds (varies by system and network):
- **Small files (<100 emails)**: 1-5 minutes
- **Medium files (100-1000 emails)**: 5-30 minutes  
- **Large files (1000+ emails)**: 30+ minutes

*Note: Actual performance depends on email server response times and network conditions.*