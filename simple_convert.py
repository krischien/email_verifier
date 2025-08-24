#!/usr/bin/env python3
"""
Simple Markdown to HTML Converter
Creates a styled HTML file that can be easily converted to PDF
"""

import markdown
import os

def convert_markdown_to_html():
    """Convert the user manual from Markdown to styled HTML"""
    
    # Check if user_manual.md exists
    markdown_file = "user_manual.md"
    if not os.path.exists(markdown_file):
        print(f"❌ Error: {markdown_file} not found!")
        return False
    
    print("🔄 Converting Markdown to HTML...")
    
    try:
        # Read markdown content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        
        # Add professional CSS styling
        styled_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mail Commander Pro - User Manual</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 20px; }}
            .no-print {{ display: none; }}
            h1, h2, h3 {{ page-break-after: avoid; }}
            table {{ page-break-inside: avoid; }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 40px;
            color: #333;
            background-color: #ffffff;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-align: center;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        h3 {{
            color: #7f8c8d;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
        
        h4 {{
            color: #95a5a6;
            margin-top: 25px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        p {{
            margin: 15px 0;
            text-align: justify;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 3px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            overflow-x: auto;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 25px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 15px;
            text-align: left;
            vertical-align: top;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tr:hover {{
            background-color: #e8f4fd;
        }}
        
        ul, ol {{
            margin: 20px 0;
            padding-left: 40px;
        }}
        
        li {{
            margin: 10px 0;
            line-height: 1.7;
        }}
        
        blockquote {{
            border-left: 5px solid #3498db;
            margin: 25px 0;
            padding: 20px 25px;
            background-color: #f8f9fa;
            color: #7f8c8d;
            font-style: italic;
            border-radius: 0 8px 8px 0;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin: 30px 0;
            border: 2px solid #ecf0f1;
        }}
        
        .toc h2 {{
            border: none;
            margin-top: 0;
            color: #2c3e50;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 8px 0;
            padding: 5px 0;
        }}
        
        .toc a {{
            text-decoration: none;
            color: #3498db;
            font-weight: 500;
            padding: 5px 10px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        
        .toc a:hover {{
            background-color: #e8f4fd;
            text-decoration: underline;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #ffc107;
            margin: 25px 0;
        }}
        
        .warning {{
            background-color: #f8d7da;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #dc3545;
            margin: 25px 0;
        }}
        
        .success {{
            background-color: #d4edda;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #28a745;
            margin: 25px 0;
        }}
        
        .info {{
            background-color: #d1ecf1;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #17a2b8;
            margin: 25px 0;
        }}
        
        .step {{
            background-color: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            margin: 20px 0;
        }}
        
        .step-number {{
            background-color: #3498db;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }}
        
        .feature-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        
        .feature-item {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #ecf0f1;
            text-align: center;
        }}
        
        .feature-icon {{
            font-size: 2em;
            margin-bottom: 15px;
        }}
        
        .print-instructions {{
            background-color: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #3498db;
            margin: 30px 0;
            text-align: center;
        }}
        
        .print-instructions h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        
        .print-instructions ul {{
            text-align: left;
            display: inline-block;
        }}
        
        @media print {{
            .print-instructions {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-instructions no-print">
        <h3>📖 How to Convert to PDF</h3>
        <p>To create a PDF from this HTML file:</p>
        <ul>
            <li><strong>Chrome/Edge:</strong> Press Ctrl+P → Save as PDF</li>
            <li><strong>Firefox:</strong> Press Ctrl+P → Save to File → PDF</li>
            <li><strong>Online:</strong> Use online HTML to PDF converters</li>
        </ul>
    </div>
    
    {html_content}
    
    <div class="print-instructions no-print">
        <h3>🎉 Mail Commander Pro User Manual</h3>
        <p>This manual covers all features and operations of Mail Commander Pro.</p>
        <p><strong>Version:</strong> 1.0 | <strong>Generated:</strong> {os.popen('date /t').read().strip()}</p>
    </div>
</body>
</html>
        """
        
        # Save HTML file
        output_file = "Mail_Commander_Pro_User_Manual.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(styled_html)
        
        if os.path.exists(output_file):
            print(f"✅ HTML file created successfully: {output_file}")
            print(f"📁 File location: {os.path.abspath(output_file)}")
            return True
        else:
            print("❌ HTML file creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Mail Commander Pro - HTML Converter")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("user_manual.md"):
        print("❌ Please run this script from the directory containing user_manual.md")
        return
    
    # Convert markdown to HTML
    success = convert_markdown_to_html()
    
    if success:
        print("\n🎉 Conversion completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Open the HTML file in your web browser")
        print("2. Press Ctrl+P to open print dialog")
        print("3. Select 'Save as PDF' as destination")
        print("4. Choose your save location and click Save")
        print("\n💡 Alternative methods:")
        print("- Use online HTML to PDF converters")
        print("- Use browser extensions for PDF conversion")
        print("- Use desktop PDF conversion software")
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
