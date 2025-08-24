#!/usr/bin/env python3
"""
AI-powered email message creator for Mail Commander Pro
Supports multiple AI providers with configurable settings
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMessageCreator:
    """AI-powered email message creator with multiple provider support"""
    
    def __init__(self, provider: str = "openai", api_key: str = None, config: Dict = None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.config = config or {}
        self.providers = self._get_provider_configs()
        
        # Validate provider
        if self.provider not in self.providers:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported: {list(self.providers.keys())}")
        
        # Set API key
        if not self.api_key:
            self.api_key = self._get_api_key_from_env()
        
        if not self.api_key:
            raise ValueError(f"API key required for {self.provider}")
    
    def _get_provider_configs(self) -> Dict[str, Dict]:
        """Get configuration for all supported AI providers"""
        return {
            'openai': {
                'name': 'OpenAI GPT',
                'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'default_model': 'gpt-4',
                'base_url': 'https://api.openai.com/v1',
                'endpoint': '/chat/completions',
                'headers': lambda key: {
                    'Authorization': f'Bearer {key}',
                    'Content-Type': 'application/json'
                },
                'rate_limit': 60,  # requests per minute
                'cost_per_1k_tokens': 0.03,  # GPT-4 cost estimate
                'max_tokens': 4000
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'default_model': 'claude-3-sonnet',
                'base_url': 'https://api.anthropic.com',
                'endpoint': '/v1/messages',
                'headers': lambda key: {
                    'x-api-key': key,
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                'rate_limit': 50,
                'cost_per_1k_tokens': 0.015,
                'max_tokens': 4000
            },
            'google': {
                'name': 'Google Gemini',
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'default_model': 'gemini-pro',
                'base_url': 'https://generativelanguage.googleapis.com/v1beta',
                'endpoint': '/models/gemini-pro:generateContent',
                'headers': lambda key: {
                    'Content-Type': 'application/json'
                },
                'rate_limit': 60,
                'cost_per_1k_tokens': 0.0005,
                'max_tokens': 8000
            },
            'local': {
                'name': 'Local Model (Ollama)',
                'models': ['llama2', 'mistral', 'codellama'],
                'default_model': 'llama2',
                'base_url': 'http://localhost:11434',
                'endpoint': '/api/generate',
                'headers': lambda key: {
                    'Content-Type': 'application/json'
                },
                'rate_limit': 100,
                'cost_per_1k_tokens': 0.0,
                'max_tokens': 4000
            }
        }
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variables"""
        env_vars = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'local': 'OLLAMA_API_KEY'  # Usually not needed for local
        }
        
        env_var = env_vars.get(self.provider)
        if env_var:
            return os.getenv(env_var)
        return None
    
    def generate_email(self, prompt: str, tone: str = "professional", 
                      length: str = "medium", industry: str = "general",
                      target_audience: str = "customers") -> Dict[str, Any]:
        """
        Generate email content using AI
        
        Args:
            prompt: User's description of the email
            tone: professional, casual, friendly, urgent, persuasive
            length: short, medium, long
            industry: ecommerce, b2b, saas, education, etc.
            target_audience: customers, prospects, employees, etc.
        
        Returns:
            Dict with generated content and metadata
        """
        try:
            # Build structured prompt
            structured_prompt = self._build_structured_prompt(
                prompt, tone, length, industry, target_audience
            )
            
            # Generate content based on provider
            if self.provider == 'openai':
                return self._generate_openai(structured_prompt)
            elif self.provider == 'anthropic':
                return self._generate_anthropic(structured_prompt)
            elif self.provider == 'google':
                return self._generate_google(structured_prompt)
            elif self.provider == 'local':
                return self._generate_local(structured_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to generate email: {str(e)}',
                'subject': '',
                'body': '',
                'suggestions': []
            }
    
    def _build_structured_prompt(self, prompt: str, tone: str, length: str, 
                                industry: str, target_audience: str) -> str:
        """Build a structured prompt for the AI"""
        
        # Define tone descriptions
        tone_descriptions = {
            'professional': 'formal and business-like',
            'casual': 'friendly and relaxed',
            'friendly': 'warm and approachable',
            'urgent': 'time-sensitive and compelling',
            'persuasive': 'convincing and action-oriented'
        }
        
        # Define length guidelines
        length_guidelines = {
            'short': 'Keep it concise, under 100 words',
            'medium': 'Standard length, 150-250 words',
            'long': 'Detailed and comprehensive, 300+ words'
        }
        
        structured_prompt = f"""
Create an email with the following specifications:

USER REQUEST: {prompt}

STYLE GUIDELINES:
- Tone: {tone_descriptions.get(tone, tone)} ({tone})
- Length: {length_guidelines.get(length, length)}
- Industry: {industry}
- Target Audience: {target_audience}

REQUIREMENTS:
1. Generate a compelling subject line (under 60 characters)
2. Create email body with appropriate greeting, content, and closing
3. Include personalization placeholders like {{name}}, {{company}}, etc.
4. Add a clear call-to-action
5. Make it engaging and relevant to the target audience

OUTPUT FORMAT:
- Subject: [subject line]
- Body: [email body]
- Personalization Fields: [list of placeholders used]
- Call-to-Action: [specific action requested]

Please ensure the email is well-structured, professional, and follows email marketing best practices.
"""
        return structured_prompt.strip()
    
    def _generate_openai(self, prompt: str) -> Dict[str, Any]:
        """Generate email using OpenAI API"""
        provider_config = self.providers['openai']
        model = self.config.get('model', provider_config['default_model'])
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert email marketing copywriter. Create compelling, professional emails that drive engagement and conversions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": provider_config['max_tokens'],
            "temperature": self.config.get('temperature', 0.7)
        }
        
        headers = provider_config['headers'](self.api_key)
        url = f"{provider_config['base_url']}{provider_config['endpoint']}"
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        return self._parse_ai_response(content, 'openai', model)
    
    def _generate_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Generate email using Anthropic Claude API"""
        provider_config = self.providers['anthropic']
        model = self.config.get('model', provider_config['default_model'])
        
        payload = {
            "model": model,
            "max_tokens": provider_config['max_tokens'],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        headers = provider_config['headers'](self.api_key)
        url = f"{provider_config['base_url']}{provider_config['endpoint']}"
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['content'][0]['text']
        
        return self._parse_ai_response(content, 'anthropic', model)
    
    def _generate_google(self, prompt: str) -> Dict[str, Any]:
        """Generate email using Google Gemini API"""
        provider_config = self.providers['google']
        model = self.config.get('model', provider_config['default_model'])
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": provider_config['max_tokens'],
                "temperature": self.config.get('temperature', 0.7)
            }
        }
        
        headers = provider_config['headers'](self.api_key)
        url = f"{provider_config['base_url']}/models/{model}:generateContent?key={self.api_key}"
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['candidates'][0]['content']['parts'][0]['text']
        
        return self._parse_ai_response(content, 'google', model)
    
    def _generate_local(self, prompt: str) -> Dict[str, Any]:
        """Generate email using local Ollama model"""
        provider_config = self.providers['local']
        model = self.config.get('model', provider_config['default_model'])
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.get('temperature', 0.7),
                "num_predict": provider_config['max_tokens']
            }
        }
        
        headers = provider_config['headers'](self.api_key)
        url = f"{provider_config['base_url']}{provider_config['endpoint']}"
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['response']
        
        return self._parse_ai_response(content, 'local', model)
    
    def _parse_ai_response(self, content: str, provider: str, model: str) -> Dict[str, Any]:
        """Parse AI response and extract email components"""
        try:
            # Try to extract structured content
            lines = content.split('\n')
            subject = ""
            body = ""
            personalization_fields = []
            call_to_action = ""
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith('subject:'):
                    subject = line.split(':', 1)[1].strip()
                elif line.lower().startswith('body:'):
                    current_section = 'body'
                elif line.lower().startswith('personalization fields:'):
                    current_section = 'personalization'
                elif line.lower().startswith('call-to-action:'):
                    call_to_action = line.split(':', 1)[1].strip()
                elif current_section == 'body':
                    body += line + '\n'
                elif current_section == 'personalization':
                    if line.startswith('-') or line.startswith('*'):
                        field = line.lstrip('- *').strip()
                        if field:
                            personalization_fields.append(field)
            
            # If structured parsing failed, try to extract subject from first line
            if not subject and lines:
                first_line = lines[0].strip()
                if len(first_line) <= 60 and not first_line.lower().startswith(('subject:', 'body:')):
                    subject = first_line
                    # Remove subject line from body
                    if body.startswith(first_line):
                        body = body[len(first_line):].strip()
            
            # Clean up body
            body = body.strip()
            
            # Generate suggestions if content is missing
            suggestions = []
            if not subject:
                suggestions.append("Consider adding a compelling subject line")
            if not body:
                suggestions.append("Email body could be more detailed")
            if not call_to_action:
                suggestions.append("Include a clear call-to-action")
            
            return {
                'status': 'success',
                'provider': provider,
                'model': model,
                'subject': subject,
                'body': body,
                'personalization_fields': personalization_fields,
                'call_to_action': call_to_action,
                'suggestions': suggestions,
                'raw_content': content,
                'timestamp': datetime.now().isoformat(),
                'estimated_cost': self._calculate_cost(len(content), provider)
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to parse AI response: {str(e)}',
                'subject': '',
                'body': '',
                'suggestions': ['Content parsing failed'],
                'raw_content': content
            }
    
    def _calculate_cost(self, content_length: int, provider: str) -> float:
        """Calculate estimated cost for the generated content"""
        if provider not in self.providers:
            return 0.0
        
        provider_config = self.providers[provider]
        tokens_estimate = content_length / 4  # Rough estimate: 1 token ≈ 4 characters
        cost = (tokens_estimate / 1000) * provider_config['cost_per_1k_tokens']
        return round(cost, 4)
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        if self.provider not in self.providers:
            return {}
        
        provider_config = self.providers[self.provider]
        return {
            'name': provider_config['name'],
            'models': provider_config['models'],
            'current_model': self.config.get('model', provider_config['default_model']),
            'rate_limit': provider_config['rate_limit'],
            'cost_per_1k_tokens': provider_config['cost_per_1k_tokens'],
            'max_tokens': provider_config['max_tokens']
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the AI provider"""
        try:
            # Try to generate a simple test email
            test_result = self.generate_email(
                "Create a simple test email saying 'Hello World'",
                tone="casual",
                length="short"
            )
            
            if test_result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': f'Successfully connected to {self.providers[self.provider]["name"]}',
                    'provider': self.provider,
                    'model': test_result.get('model', 'Unknown')
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Connection test failed: {test_result.get("message", "Unknown error")}',
                    'provider': self.provider
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'provider': self.provider
            }
    
    def get_available_providers(self) -> Dict[str, Dict]:
        """Get information about all available providers"""
        return self.providers.copy()

# Pre-built prompt templates
EMAIL_TEMPLATES = {
    'welcome': {
        'name': 'Welcome Email',
        'prompt': 'Create a welcome email for new customers who just signed up',
        'tone': 'friendly',
        'length': 'medium'
    },
    'follow_up': {
        'name': 'Follow-up Email',
        'prompt': 'Create a follow-up email to re-engage customers who haven\'t opened recent emails',
        'tone': 'friendly',
        'length': 'short'
    },
    'product_launch': {
        'name': 'Product Launch',
        'prompt': 'Create an exciting product launch announcement email',
        'tone': 'urgent',
        'length': 'medium'
    },
    'abandoned_cart': {
        'name': 'Abandoned Cart',
        'prompt': 'Create an abandoned cart recovery email with a special offer',
        'tone': 'persuasive',
        'length': 'short'
    },
    'newsletter': {
        'name': 'Newsletter',
        'prompt': 'Create a monthly newsletter email with industry insights and company updates',
        'tone': 'professional',
        'length': 'long'
    },
    'promotion': {
        'name': 'Promotion/Sale',
        'prompt': 'Create a promotional email announcing a limited-time sale or discount',
        'tone': 'urgent',
        'length': 'medium'
    }
}

# Industry-specific templates
INDUSTRY_TEMPLATES = {
    'ecommerce': {
        'name': 'E-commerce',
        'templates': ['welcome', 'abandoned_cart', 'product_launch', 'promotion', 'follow_up']
    },
    'b2b': {
        'name': 'B2B/SaaS',
        'templates': ['welcome', 'product_launch', 'newsletter', 'follow_up']
    },
    'education': {
        'name': 'Education',
        'templates': ['welcome', 'newsletter', 'follow_up']
    },
    'healthcare': {
        'name': 'Healthcare',
        'templates': ['welcome', 'newsletter', 'follow_up']
    }
}
