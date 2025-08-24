#!/usr/bin/env python3
"""
Convert Markdown User Manual to PDF
Converts the user_manual.md file to a professional PDF document
"""

import os
import sys
from pathlib import Path

def convert_markdown_to_pdf():
    """Convert the user manual from Markdown to PDF"""
    
    # Check if user_manual.md exists
    markdown_file = "user_manual.md"
    if not os.path.exists(markdown_file):
        print(f"❌ Error: {markdown_file} not found!")
        return False
    
    print("🔄 Converting Markdown to PDF...")
    
    try:
        # Try using markdown2pdf first
        try:
            import markdown2pdf
            print("📚 Using markdown2pdf...")
            
            # Convert markdown to PDF
            output_file = "Mail_Commander_Pro_User_Manual.pdf"
            markdown2pdf.convert(markdown_file, output_file)
            
            if os.path.exists(output_file):
                print(f"✅ PDF created successfully: {output_file}")
                return True
            else:
                print("❌ PDF creation failed with markdown2pdf")
                raise ImportError("markdown2pdf failed")
                
        except ImportError:
            print("📚 markdown2pdf not available, trying alternative methods...")
            
            # Alternative: Use weasyprint with markdown
            try:
                import markdown
                import weasyprint
                
                print("📚 Using markdown + weasyprint...")
                
                # Read markdown content
                with open(markdown_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Convert markdown to HTML
                html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
                
                # Add CSS styling
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Mail Commander Pro - User Manual</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            line-height: 1.6;
                            margin: 40px;
                            color: #333;
                        }}
                        h1 {{
                            color: #2c3e50;
                            border-bottom: 3px solid #3498db;
                            padding-bottom: 10px;
                        }}
                        h2 {{
                            color: #34495e;
                            border-bottom: 2px solid #ecf0f1;
                            padding-bottom: 5px;
                            margin-top: 30px;
                        }}
                        h3 {{
                            color: #7f8c8d;
                            margin-top: 25px;
                        }}
                        h4 {{
                            color: #95a5a6;
                            margin-top: 20px;
                        }}
                        code {{
                            background-color: #f8f9fa;
                            padding: 2px 4px;
                            border-radius: 3px;
                            font-family: 'Courier New', monospace;
                        }}
                        pre {{
                            background-color: #f8f9fa;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #3498db;
                            overflow-x: auto;
                        }}
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }}
                        th, td {{
                            border: 1px solid #ddd;
                            padding: 12px;
                            text-align: left;
                        }}
                        th {{
                            background-color: #f2f2f2;
                            font-weight: bold;
                        }}
                        ul, ol {{
                            margin: 15px 0;
                            padding-left: 30px;
                        }}
                        li {{
                            margin: 8px 0;
                        }}
                        blockquote {{
                            border-left: 4px solid #3498db;
                            margin: 20px 0;
                            padding-left: 20px;
                            color: #7f8c8d;
                            font-style: italic;
                        }}
                        .toc {{
                            background-color: #f8f9fa;
                            padding: 20px;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                        .toc ul {{
                            list-style-type: none;
                            padding-left: 0;
                        }}
                        .toc li {{
                            margin: 5px 0;
                        }}
                        .toc a {{
                            text-decoration: none;
                            color: #3498db;
                        }}
                        .toc a:hover {{
                            text-decoration: underline;
                        }}
                        .highlight {{
                            background-color: #fff3cd;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #ffc107;
                            margin: 20px 0;
                        }}
                        .warning {{
                            background-color: #f8d7da;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #dc3545;
                            margin: 20px 0;
                        }}
                        .success {{
                            background-color: #d4edda;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #28a745;
                            margin: 20px 0;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                # Convert HTML to PDF
                output_file = "Mail_Commander_Pro_User_Manual.pdf"
                weasyprint.HTML(string=styled_html).write_pdf(output_file)
                
                if os.path.exists(output_file):
                    print(f"✅ PDF created successfully: {output_file}")
                    return True
                else:
                    print("❌ PDF creation failed with weasyprint")
                    raise ImportError("weasyprint failed")
                    
            except ImportError:
                print("📚 weasyprint not available, trying final alternative...")
                
                # Final alternative: Use markdown + pdfkit (requires wkhtmltopdf)
                try:
                    import markdown
                    import pdfkit
                    
                    print("📚 Using markdown + pdfkit...")
                    
                    # Read markdown content
                    with open(markdown_file, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                    
                    # Convert markdown to HTML
                    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
                    
                    # Add basic styling
                    styled_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <title>Mail Commander Pro - User Manual</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                            h2 {{ color: #34495e; margin-top: 30px; }}
                            h3 {{ color: #7f8c8d; margin-top: 25px; }}
                            code {{ background-color: #f8f9fa; padding: 2px 4px; }}
                            pre {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }}
                            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                            th {{ background-color: #f2f2f2; }}
                        </style>
                    </head>
                    <body>
                        {html_content}
                    </body>
                    </html>
                    """
                    
                    # Convert HTML to PDF
                    output_file = "Mail_Commander_Pro_User_Manual.pdf"
                    pdfkit.from_string(styled_html, output_file)
                    
                    if os.path.exists(output_file):
                        print(f"✅ PDF created successfully: {output_file}")
                        return True
                    else:
                        print("❌ PDF creation failed with pdfkit")
                        raise ImportError("pdfkit failed")
                        
                except ImportError:
                    print("❌ No PDF conversion libraries available!")
                    print("\n📋 To install PDF conversion libraries, run one of these commands:")
                    print("   pip install markdown2pdf")
                    print("   pip install weasyprint")
                    print("   pip install pdfkit")
                    print("\n💡 Note: pdfkit requires wkhtmltopdf to be installed separately")
                    return False
                    
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Mail Commander Pro - PDF Converter")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("user_manual.md"):
        print("❌ Please run this script from the directory containing user_manual.md")
        return
    
    # Convert markdown to PDF
    success = convert_markdown_to_pdf()
    
    if success:
        print("\n🎉 Conversion completed successfully!")
        print("📁 Check your current directory for the PDF file")
        print("📖 File: Mail_Commander_Pro_User_Manual.pdf")
    else:
        print("\n💡 Alternative conversion methods:")
        print("1. Use online Markdown to PDF converters")
        print("2. Open in Typora and export to PDF")
        print("3. Use VS Code with Markdown PDF extension")
        print("4. Use Pandoc: pandoc user_manual.md -o manual.pdf")

if __name__ == "__main__":
    main()
