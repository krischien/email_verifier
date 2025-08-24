#!/usr/bin/env python3
"""
Simple test script to verify all components are working
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import dns.resolver
        print("✓ dns.resolver imported successfully")
    except ImportError as e:
        print(f"✗ dns.resolver import failed: {e}")
        return False
    
    try:
        from email_validator import validate_email
        print("✓ email_validator imported successfully")
    except ImportError as e:
        print(f"✗ email_validator import failed: {e}")
        return False
    
    try:
        from email_verifier import EmailVerifier
        print("✓ email_verifier imported successfully")
    except ImportError as e:
        print(f"✗ email_verifier import failed: {e}")
        return False
    
    try:
        from csv_processor import CSVProcessor
        print("✓ csv_processor imported successfully")
    except ImportError as e:
        print(f"✗ csv_processor import failed: {e}")
        return False
    
    return True

def test_email_verifier():
    """Test basic email verification functionality"""
    print("\nTesting email verifier...")
    
    try:
        from email_verifier import EmailVerifier
        
        verifier = EmailVerifier(max_workers=2)
        
        # Test format validation
        test_emails = [
            "test@example.com",
            "invalid-email",
            "user@domain",
            "admin@gmail.com"
        ]
        
        print("Testing individual email verification...")
        for email in test_emails:
            result = verifier.verify_single_email(email)
            print(f"  {email}: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Email verifier test failed: {e}")
        return False

def test_csv_processor():
    """Test CSV processing functionality"""
    print("\nTesting CSV processor...")
    
    try:
        from csv_processor import CSVProcessor
        
        processor = CSVProcessor()
        
        # Test with sample file
        if os.path.exists("sample_emails.csv"):
            is_valid, message = processor.validate_file("sample_emails.csv")
            print(f"Sample file validation: {message}")
            
            if is_valid:
                df, email_column = processor.read_csv_file("sample_emails.csv")
                emails = processor.extract_emails(df, email_column)
                print(f"Extracted {len(emails)} emails from column '{email_column}'")
                return True
            else:
                print(f"Sample file validation failed: {message}")
                return False
        else:
            print("Sample file not found, skipping CSV test")
            return True
            
    except Exception as e:
        print(f"✗ CSV processor test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\nTesting basic functionality...")
    
    try:
        # Test email format validation
        from email_validator import validate_email, EmailNotValidError
        
        test_cases = [
            ("valid@example.com", True),
            ("invalid-email", False),
            ("user@domain", False),
            ("test@gmail.com", True)
        ]
        
        for email, expected in test_cases:
            try:
                validate_email(email)
                result = True
            except EmailNotValidError:
                result = False
            
            if result == expected:
                print(f"✓ {email}: {result}")
            else:
                print(f"✗ {email}: expected {expected}, got {result}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Email Verifier Pro - Component Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Email Verifier", test_email_verifier),
        ("CSV Processor", test_csv_processor)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            print(f"✓ {test_name} passed")
            passed += 1
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python main_app.py' for the GUI version")
        print("2. Run 'python cli_version.py sample_emails.csv' for CLI testing")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
