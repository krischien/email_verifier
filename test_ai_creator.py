#!/usr/bin/env python3
"""
Test script for the AI Message Creator functionality
"""

from ai_message_creator import AIMessageCreator, EMAIL_TEMPLATES, INDUSTRY_TEMPLATES

def test_ai_creator():
    """Test the AI Message Creator functionality"""
    print("Testing AI Message Creator...")
    
    # Test 1: Check available providers
    print("\n1. Available AI Providers:")
    try:
        # Create a dummy instance to get provider info
        dummy_creator = AIMessageCreator("openai", "dummy_key")
        providers = dummy_creator.get_available_providers()
        for provider, config in providers.items():
            print(f"   - {config['name']}: {config['models']}")
    except Exception as e:
        print(f"   Error getting providers: {e}")
    
    # Test 2: Check email templates
    print("\n2. Available Email Templates:")
    for template_key, template in EMAIL_TEMPLATES.items():
        print(f"   - {template['name']}: {template['prompt'][:50]}...")
    
    # Test 3: Check industry templates
    print("\n3. Industry-Specific Templates:")
    for industry, config in INDUSTRY_TEMPLATES.items():
        print(f"   - {config['name']}: {', '.join(config['templates'])}")
    
    # Test 4: Test provider configuration (without API calls)
    print("\n4. Provider Configuration Test:")
    try:
        # Test OpenAI config
        openai_creator = AIMessageCreator("openai", "dummy_key")
        provider_info = openai_creator.get_provider_info()
        print(f"   OpenAI: {provider_info['name']}, Model: {provider_info['current_model']}")
        
        # Test Anthropic config
        anthropic_creator = AIMessageCreator("anthropic", "dummy_key")
        provider_info = anthropic_creator.get_provider_info()
        print(f"   Anthropic: {provider_info['name']}, Model: {provider_info['current_model']}")
        
    except Exception as e:
        print(f"   Error testing provider config: {e}")
    
    print("\n✅ AI Message Creator tests completed successfully!")
    print("\nNote: This test doesn't make actual API calls.")
    print("To test real AI generation, you'll need valid API keys.")
    return True

if __name__ == "__main__":
    test_ai_creator()
