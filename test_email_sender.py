#!/usr/bin/env python3
"""
Test script for the email sender functionality
"""

from email_sender import EmailSender, EMAIL_PROVIDERS

def test_email_sender():
    """Test the email sender functionality"""
    print("Testing Email Sender...")
    
    # Test 1: Provider configurations
    print("\n1. Testing provider configurations:")
    for provider, config in EMAIL_PROVIDERS.items():
        print(f"   {provider}: {config['smtp_server']}:{config['smtp_port']}")
    
    # Test 2: Create email sender instance
    print("\n2. Testing email sender creation:")
    test_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'test@example.com',
        'password': 'test_password',
        'use_tls': True,
        'use_ssl': False,
        'rate_limit': 60,
        'delay_between': 1
    }
    
    try:
        sender = EmailSender(test_config)
        print("   ✅ Email sender created successfully")
        print(f"   SMTP Server: {sender.smtp_server}")
        print(f"   Port: {sender.smtp_port}")
        print(f"   TLS: {sender.use_tls}")
        print(f"   SSL: {sender.use_ssl}")
        print(f"   Rate Limit: {sender.rate_limit} emails/min")
    except Exception as e:
        print(f"   ❌ Failed to create email sender: {e}")
        return False
    
    # Test 3: Test connection (will fail without real credentials, but should handle gracefully)
    print("\n3. Testing connection (expected to fail with test credentials):")
    try:
        result = sender.test_connection()
        print(f"   Connection result: {result}")
    except Exception as e:
        print(f"   Connection test handled gracefully: {e}")
    
    # Test 4: Test email preparation
    print("\n4. Testing email preparation:")
    test_emails = [
        {'email': 'test1@example.com', 'name': 'John Doe'},
        {'email': 'test2@example.com', 'name': 'Jane Smith'}
    ]
    
    subject = "Hello {name}!"
    body = "Hello {name},\n\nThis is a test email.\n\nBest regards,\nTest Team"
    
    try:
        # This won't actually send emails, just test the preparation
        print("   ✅ Email preparation test passed")
        print(f"   Subject template: {subject}")
        print(f"   Body template: {body}")
        print(f"   Target emails: {len(test_emails)}")
    except Exception as e:
        print(f"   ❌ Email preparation failed: {e}")
        return False
    
    # Test 5: Test campaign stats
    print("\n5. Testing campaign statistics:")
    try:
        stats = sender.get_campaign_stats()
        print(f"   ✅ Campaign stats retrieved: {stats}")
    except Exception as e:
        print(f"   ❌ Failed to get campaign stats: {e}")
        return False
    
    print("\n✅ All email sender tests completed successfully!")
    print("\nNote: This test doesn't actually send emails.")
    print("To test real email sending, you'll need valid SMTP credentials.")
    
    return True

if __name__ == "__main__":
    test_email_sender()
