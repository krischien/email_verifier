# Mail Commander Pro - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Email Verification Tab](#email-verification-tab)
4. [AI Message Creator Tab](#ai-message-creator-tab)
5. [Campaign Commander Tab](#campaign-commander-tab)
6. [Workflow Examples](#workflow-examples)
7. [Troubleshooting](#troubleshooting)
8. [Tips and Best Practices](#tips-and-best-practices)

---

## Introduction

**Mail Commander Pro** is a comprehensive email management and marketing solution that combines email verification, AI-powered content creation, and bulk email campaigns in one powerful application.

### Key Features
- **Email Verification**: Validate email addresses for format, MX records, and SMTP connectivity
- **AI Message Creator**: Generate compelling email content using multiple AI providers
- **Campaign Commander**: Send bulk email campaigns with professional SMTP integration
- **Multi-file Support**: Process multiple CSV/Excel files simultaneously
- **Progress Tracking**: Real-time progress monitoring with cancellation support
- **Export Results**: Download verification results in various formats

---

## Getting Started

### System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Internet connection for AI features and email sending

### Installation
1. Download `MailCommanderPro.exe` from the distribution folder
2. Place the executable in your desired location
3. Double-click to run (no installation required)

### First Launch
- The application will open with three tabs
- All tabs are fully functional from the start
- No initial configuration required for basic features

---

## Email Verification Tab

### Purpose
Validate email addresses from CSV/Excel files to ensure deliverability and identify valid leads.

### Step-by-Step Operation

#### 1. File Selection
- **Add Files**: Click to select multiple CSV/Excel files
- **Clear All**: Remove all selected files
- **Remove Selected**: Remove specific files from the list
- **File Info**: Shows total emails and file sizes

#### 2. Verification Settings
- **Max Concurrent Workers**: Number of simultaneous verification processes (default: 20)
- **Fast Mode**: Faster verification with slightly less thorough checks (recommended)
- **SMTP Timeout**: Connection timeout in seconds (default: 5)

#### 3. Starting Verification
1. Select your CSV/Excel files
2. Adjust settings if needed
3. Click **"Start Verification"**
4. Monitor progress in real-time
5. Use **"Cancel"** to stop mid-process if needed

#### 4. Results Display
The results table shows:
- **Email**: Email address
- **Format**: Syntax validation (✓/✗)
- **MX**: DNS record check (✓/✗)
- **Ping**: SMTP connection test result
- **Status**: Overall validation result
- **Source File**: Which file the email came from

#### 5. Download Options
- **Download All Leads**: Complete verification results
- **Download Valid Only**: Only verified valid emails
- **Download Risky Only**: Emails that accept everything
- **Download Valid + Risky**: Combined valid and risky emails

### File Format Requirements
- **CSV**: Comma-separated values
- **Excel**: .xlsx or .xls files
- **Email Column**: Automatically detected
- **Headers**: First row should contain column names

---

## AI Message Creator Tab

### Purpose
Generate professional email content using AI technology with multiple provider support.

### Step-by-Step Operation

#### 1. AI Configuration (Left Side)
- **AI Provider**: Select from OpenAI, Anthropic, Google, or Local
- **API Key**: Enter your provider's API key
- **Test Connection**: Verify API connectivity

#### 2. AI Settings (Right Side)
- **Model**: Choose the AI model (varies by provider)
- **Temperature**: Creativity level (0.0 = focused, 1.0 = creative)
- **Tone**: Professional, casual, friendly, urgent, or persuasive
- **Length**: Short, medium, or long content
- **Industry**: General, ecommerce, B2B, SaaS, education, healthcare
- **Target Audience**: Customers, prospects, employees, partners

#### 3. Quick Templates
Pre-built templates for common scenarios:
- **Welcome**: New customer onboarding
- **Follow-up**: Post-interaction communication
- **Product Launch**: New product announcements
- **Abandoned Cart**: E-commerce recovery
- **Newsletter**: Regular updates
- **Promotion**: Special offers

#### 4. Content Generation
1. Select or customize AI settings
2. Enter email description in the prompt field
3. Click **"Generate Email"**
4. Review generated subject and body
5. Use **"Refine Content"** for improvements
6. Click **"Send to Campaign Commander"** to transfer content

#### 5. Generated Content
- **Subject Line**: AI-generated email subject
- **Email Body**: Complete email content
- **Cost Tracking**: Estimated API usage costs
- **Suggestions**: AI recommendations for improvement

---

## Campaign Commander Tab

### Purpose
Send bulk email campaigns to verified email addresses with professional SMTP integration.

### Step-by-Step Operation

#### 1. Email Provider Configuration
- **Email Provider**: Pre-configured settings for popular providers
- **SMTP Server**: Mail server address (auto-filled for providers)
- **Port**: Connection port (auto-filled for providers)

#### 2. Connection Settings
- **Username**: Your email address
- **Password**: Your email password or app-specific password
- **Use TLS**: Enable Transport Layer Security (recommended)
- **Use SSL**: Enable Secure Sockets Layer (alternative to TLS)
- **Rate Limit**: Emails per minute (default: 60)

#### 3. Testing Connection
1. Enter your credentials
2. Click **"Test Connection"**
3. Verify successful connection
4. Status will show green for success

#### 4. Email Content
- **Subject**: Email subject line (can be personalized with {name})
- **Body**: Email content (supports personalization)
- **Personalization**: Use {name} placeholder for recipient names

#### 5. Sending Campaigns
1. Ensure emails are verified in the Email Verification tab
2. Configure your SMTP settings
3. Write or import email content
4. Choose target audience:
   - **Send to Valid Emails**: Only verified valid addresses
   - **Send to Valid + Risky**: Include potentially valid addresses
5. Monitor progress with real-time updates
6. Use **"Cancel Sending"** to stop mid-campaign

### SMTP Provider Setup

#### Gmail
- **SMTP Server**: smtp.gmail.com
- **Port**: 587
- **Use TLS**: Yes
- **App Password**: Use app-specific password, not regular password

#### Outlook/Hotmail
- **SMTP Server**: smtp-mail.outlook.com
- **Port**: 587
- **Use TLS**: Yes

#### Yahoo
- **SMTP Server**: smtp.mail.yahoo.com
- **Port**: 587
- **Use TLS**: Yes

#### Custom SMTP
- **SMTP Server**: Your server address
- **Port**: Your server port
- **Security**: Configure based on your server requirements

---

## Workflow Examples

### Complete Email Marketing Workflow

#### 1. Lead Verification
1. Open **Email Verification** tab
2. Add CSV files with email lists
3. Start verification process
4. Download valid email results

#### 2. Content Creation
1. Switch to **AI Message Creator** tab
2. Configure AI provider and settings
3. Generate email content
4. Refine content if needed
5. Send to Campaign Commander

#### 3. Campaign Execution
1. Switch to **Campaign Commander** tab
2. Configure SMTP settings
3. Review imported content
4. Send campaign to verified emails
5. Monitor progress and results

### Quick Template Workflow
1. Select template in AI Message Creator
2. Customize settings for your industry
3. Generate content
4. Transfer to Campaign Commander
5. Send immediately

---

## Troubleshooting

### Common Issues and Solutions

#### Email Verification Issues
- **"No valid files selected"**: Check file format and ensure email column exists
- **"Connection timeout"**: Increase SMTP timeout in settings
- **"Verification failed"**: Check internet connection and try reducing worker count

#### AI Generation Issues
- **"API key required"**: Enter valid API key for selected provider
- **"Connection failed"**: Verify API key and internet connection
- **"Generation failed"**: Check prompt length and try again

#### Email Sending Issues
- **"Authentication failed"**: Verify username/password and enable 2FA if required
- **"Connection refused"**: Check SMTP server and port settings
- **"Rate limit exceeded"**: Reduce emails per minute setting

### Performance Optimization
- **Fast Mode**: Enable for quicker verification
- **Worker Count**: Adjust based on your system capabilities
- **Batch Size**: Process files in smaller batches for large datasets

---

## Tips and Best Practices

### Email Verification
- **Verify before sending**: Always verify emails before campaigns
- **Use Fast Mode**: Balance speed and accuracy
- **Regular updates**: Re-verify email lists periodically
- **Export results**: Keep verification records for compliance

### AI Content Creation
- **Clear prompts**: Be specific about your requirements
- **Test different tones**: Experiment with various communication styles
- **Refine content**: Use AI suggestions for improvement
- **Cost management**: Monitor API usage and costs

### Email Campaigns
- **Personalization**: Use recipient names when possible
- **Rate limiting**: Respect email provider limits
- **Content testing**: Test emails before bulk sending
- **Compliance**: Follow email marketing regulations (CAN-SPAM, GDPR)

### General Application
- **Save configurations**: Keep your settings for future use
- **Regular backups**: Export important data regularly
- **Update regularly**: Check for application updates
- **Support**: Keep track of your API keys and credentials

---

## Support and Resources

### Application Information
- **Version**: Mail Commander Pro
- **Developer**: Professional Email Solutions
- **License**: Commercial Use

### Getting Help
- **Documentation**: This user manual
- **Troubleshooting**: Use the troubleshooting section above
- **Best Practices**: Follow the tips and recommendations

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB free space
- **Network**: Internet connection required

---

## Conclusion

Mail Commander Pro provides a comprehensive solution for email marketing professionals, combining powerful verification tools, AI-powered content creation, and professional campaign management. By following this manual and best practices, you can maximize the effectiveness of your email marketing efforts while maintaining high deliverability rates.

**Happy email marketing! 🚀**

---

*This manual covers Mail Commander Pro version 1.0. For updates and additional support, please refer to the latest documentation.*
