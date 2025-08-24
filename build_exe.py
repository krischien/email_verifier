import PyInstaller.__main__
import os
import sys

def build_exe():
    """Build the email verifier app into an executable"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the main script path
    main_script = os.path.join(current_dir, 'main_app.py')
    
    # Define the output directory
    output_dir = os.path.join(current_dir, 'dist')
    
    # PyInstaller arguments
    args = [
        main_script,
        '--onefile',  # Create a single executable file
        '--windowed',  # Don't show console window (Windows)
        '--name=MailCommanderPro',  # Name of the executable
        f'--distpath={output_dir}',  # Output directory
        '--add-data=requirements.txt;.',  # Include requirements file
        '--hidden-import=dns.resolver',  # Ensure DNS resolver is included
        '--hidden-import=email_validator',  # Ensure email validator is included
        '--hidden-import=pandas',  # Ensure pandas is included
        '--hidden-import=numpy',  # Ensure numpy is included (pandas dependency)
        '--hidden-import=numpy.core._methods',  # Additional numpy components
        '--hidden-import=numpy.lib.format',  # Additional numpy components
        '--exclude-module=torch',  # Exclude torch (not needed)
        '--exclude-module=tensorboard',  # Exclude tensorboard (not needed)
        '--exclude-module=matplotlib',  # Exclude matplotlib (not needed)
        '--icon=NONE',  # No icon for now (can be added later)
        '--clean',  # Clean cache before building
        '--log-level=WARN',  # Reduce log verbosity
    ]
    
    print("Building Mail Commander Pro executable...")
    print(f"Main script: {main_script}")
    print(f"Output directory: {output_dir}")
    print("PyInstaller arguments:", args)
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        print(f"\n✅ Build completed successfully!")
        print(f"Executable location: {output_dir}")
        print(f"Executable name: MailCommanderPro.exe")
        
    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    build_exe()
