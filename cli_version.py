#!/usr/bin/env python3
"""
Command-line interface for Email Verifier
Useful for testing and batch processing
"""

import argparse
import sys
import os
from email_verifier import EmailVerifier
from csv_processor import CSVProcessor
import time
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Email Verifier CLI')
    parser.add_argument('files', nargs='+', help='Path(s) to CSV/Excel file(s) containing emails')
    parser.add_argument('-o', '--output', help='Output directory for results', default='./results')
    parser.add_argument('-w', '--workers', type=int, default=20, help='Number of concurrent workers')
    parser.add_argument('--fast-mode', action='store_true', default=True, help='Enable fast mode (faster but less thorough)')
    parser.add_argument('--standard-mode', action='store_true', help='Use standard mode (slower but more thorough)')
    parser.add_argument('--timeout', type=int, default=5, help='SMTP timeout in seconds')
    parser.add_argument('--format-only', action='store_true', help='Only check email format (skip MX and SMTP)')
    parser.add_argument('--mx-only', action='store_true', help='Check format and MX records only (skip SMTP)')
    
    args = parser.parse_args()
    
    # Determine mode
    fast_mode = args.fast_mode and not args.standard_mode
    
    # Check if all input files exist
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found")
            sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    try:
        # Initialize components
        csv_processor = CSVProcessor()
        email_verifier = EmailVerifier(max_workers=args.workers, fast_mode=fast_mode, timeout=args.timeout)
        
        print(f"Processing {len(args.files)} file(s)...")
        
        # Collect all emails from all files
        all_emails = []
        file_emails_map = {}  # Track which emails came from which file
        
        for file_path in args.files:
            try:
                # Validate and read file
                is_valid, message = csv_processor.validate_file(file_path)
                if not is_valid:
                    print(f"Warning: Skipping {file_path} - {message}")
                    continue
                
                print(f"✓ {os.path.basename(file_path)}: {message}")
                
                # Read file and extract emails
                df, email_column = csv_processor.read_csv_file(file_path)
                emails = csv_processor.extract_emails(df, email_column)
                
                # Add file source information
                for email in emails:
                    if email not in file_emails_map:
                        file_emails_map[email] = file_path
                        all_emails.append(email)
                
            except Exception as e:
                print(f"Warning: Could not process {file_path}: {e}")
                continue
        
        if not all_emails:
            print("Error: No valid emails found in any of the files")
            sys.exit(1)
        
        print(f"Found {len(all_emails)} unique emails from {len(args.files)} files")
        print(f"Starting verification with {args.workers} workers...")
        print(f"Mode: {'Fast' if fast_mode else 'Standard'} (Timeout: {args.timeout}s)")
        print("-" * 50)
        
        # Progress tracking
        start_time = time.time()
        processed = 0
        
        def progress_callback(current, total):
            nonlocal processed
            processed = current
            percentage = (current / total) * 100
            elapsed = time.time() - start_time
            if current > 0:
                eta = (elapsed / current) * (total - current)
                print(f"\rProgress: {current}/{total} ({percentage:.1f}%) - ETA: {eta:.1f}s", end='', flush=True)
        
        # Start verification
        try:
            results = email_verifier.verify_emails_batch(all_emails, progress_callback)
            print("\n")  # New line after progress
            
            # Process results
            valid_count = sum(1 for r in results if r['status'] == 'valid')
            risky_count = sum(1 for r in results if r['status'] == 'risky')
            invalid_count = sum(1 for r in results if r['status'] == 'invalid')
            error_count = sum(1 for r in results if r['status'] == 'error')
            
            print("-" * 50)
            print("VERIFICATION RESULTS:")
            print(f"Total processed: {len(results)}")
            print(f"Valid: {valid_count}")
            print(f"Risky: {risky_count}")
            print(f"Invalid: {invalid_count}")
            if error_count > 0:
                print(f"Errors: {error_count}")
            
            # Show results per file
            print("\nResults by file:")
            file_stats = {}
            for result in results:
                source_file = file_emails_map.get(result['email'], 'Unknown')
                if source_file not in file_stats:
                    file_stats[source_file] = {'total': 0, 'valid': 0, 'risky': 0, 'invalid': 0}
                file_stats[source_file]['total'] += 1
                file_stats[source_file][result['status']] += 1
            
            for file_path, stats in file_stats.items():
                filename = os.path.basename(file_path)
                print(f"  {filename}: {stats['total']} emails (Valid: {stats['valid']}, Risky: {stats['risky']}, Invalid: {stats['invalid']})")
            
            # Add source file information to results
            for result in results:
                result['source_file'] = file_emails_map.get(result['email'], 'Unknown')
            
            # Save results
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # All results
            all_file = os.path.join(args.output, f"all_results_{timestamp}.csv")
            df_results = pd.DataFrame(results)
            df_results.to_csv(all_file, index=False)
            print(f"\nAll results saved to: {all_file}")
            
            # Valid only
            if valid_count > 0:
                valid_file = os.path.join(args.output, f"valid_only_{timestamp}.csv")
                df_valid = df_results[df_results['status'] == 'valid']
                df_valid.to_csv(valid_file, index=False)
                print(f"Valid emails saved to: {valid_file}")
            
            # Risky only
            if risky_count > 0:
                risky_file = os.path.join(args.output, f"risky_only_{timestamp}.csv")
                df_risky = df_results[df_results['status'] == 'risky']
                df_risky.to_csv(risky_file, index=False)
                print(f"Risky emails saved to: {risky_file}")
            
            # Valid + Risky
            if valid_count + risky_count > 0:
                valid_risky_file = os.path.join(args.output, f"valid_and_risky_{timestamp}.csv")
                df_valid_risky = df_results[df_results['status'].isin(['valid', 'risky'])]
                df_valid_risky.to_csv(valid_risky_file, index=False)
                print(f"Valid + Risky emails saved to: {valid_risky_file}")
            
            total_time = time.time() - start_time
            print(f"\nTotal time: {total_time:.2f} seconds")
            print(f"Average time per email: {total_time/len(all_emails):.2f} seconds")
            
        except KeyboardInterrupt:
            print("\n\nVerification cancelled by user")
            email_verifier.cancel_verification()
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
