# -*- coding: utf-8 -*-
"""
UC Learn Course Participant Scraper - Python 3 Self-Contained Version
Modern Python 3.6+ version with automatic dependency management
No admin rights required - installs to user directory
"""

import sys
import os
import time
import json
import tempfile
import subprocess
from pathlib import Path

def ensure_packages():
    """Ensure required packages are installed to user directory."""
    required_packages = [
        'selenium>=4.15.0',
        'beautifulsoup4>=4.12.0',
        'requests>=2.31.0',
        'webdriver-manager>=4.0.0'
    ]
    
    print("[INFO] Ensuring required packages are installed...")
    
    for package in required_packages:
        try:
            # Try to import the package first
            package_name = package.split('>=')[0].split('==')[0]
            if package_name == 'beautifulsoup4':
                import bs4
            else:
                __import__(package_name.replace('-', '_'))
            print(f"✓ {package_name} already available")
        except ImportError:
            print(f"Installing {package_name}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '--user', '--upgrade', '--quiet', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {package_name} installed successfully")
            else:
                print(f"⚠ Warning: {package_name} installation may have failed")
                print(f"Error: {result.stderr}")

def main():
    """Main function for Python 3 self-contained scraper."""
    print("=" * 60)
    print("UC LEARN SCRAPER - PYTHON 3 SELF-CONTAINED")
    print("=" * 60)
    print()
    
    # Check Python version
    if sys.version_info < (3, 6):
        print(f"[ERROR] Python {sys.version_info.major}.{sys.version_info.minor} is too old.")
        print("This script requires Python 3.6 or later.")
        print("Please upgrade from: https://python.org/downloads/")
        input("Press Enter to exit...")
        return 1
    
    print(f"[SUCCESS] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    print()
    
    # Ensure packages are installed
    try:
        ensure_packages()
    except Exception as e:
        print(f"[ERROR] Package installation failed: {e}")
        print("Please check your internet connection and try again.")
        input("Press Enter to exit...")
        return 1
    
    print()
    print("[INFO] All packages ready. Starting scraper import...")
    
    # Ensure current directory is in Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Import the scraper
    try:
        from portable_scraper import PortableUCLearnScraper
        print("✓ Scraper imported successfully")
    except ImportError as e:
        print(f"[ERROR] Could not import scraper: {e}")
        print("Make sure portable_scraper.py is in the same directory.")
        print(f"Current directory: {current_dir}")
        print(f"Python path: {sys.path}")
        input("Press Enter to exit...")
        return 1
    
    # Get course name
    if len(sys.argv) > 1:
        course_name = sys.argv[1].upper()
    else:
        course_name = input("\nEnter course name (e.g., MBAM604): ").strip().upper()
        if not course_name:
            print("No course name provided. Exiting.")
            return 1
    
    print(f"\n[INFO] Target course: {course_name}")
    print("[INFO] Initializing scraper...")
    
    # Set up portable environment
    app_dir = Path(__file__).parent
    temp_dir = Path(tempfile.gettempdir()) / "uc_scraper_python3"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"[INFO] Working directory: {app_dir}")
    print(f"[INFO] Temp directory: {temp_dir}")
    
    # Set environment variable for the scraper
    os.environ['TARGET_COURSE'] = course_name
    
    try:
        print("\n[INFO] Creating scraper instance...")
        scraper = PortableUCLearnScraper(
            headless=False,
            portable_dir=str(app_dir),
            temp_dir=str(temp_dir)
        )
        
        print("[INFO] Starting scraping process...")
        print("[INFO] Browser will open - please complete login when prompted")
        print()
        
        # Run the scraper
        success = scraper.scrape_course_participants()
        
        if success:
            print("\n[SUCCESS] Scraping completed successfully!")
            
            # Show output files
            output_files = list(app_dir.glob(f"{course_name.lower()}*"))
            if output_files:
                print("\nOutput files created:")
                for file in output_files:
                    print(f"  • {file.name}")
            else:
                print("\nCheck current directory for output files.")
            
            print(f"\n[INFO] All files saved in: {app_dir}")
            return 0
            
        else:
            print("\n[ERROR] Scraping failed.")
            print("\nTroubleshooting:")
            print("• Check internet connection")
            print("• Ensure Chrome or Firefox is installed")
            print("• Verify course name is correct")
            print("• Make sure you have access to the course")
            
            return 1
            
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user.")
        return 1
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print("\nTroubleshooting:")
        print("• Check that all files are in the same directory")
        print("• Ensure you have internet connection")
        print("• Try running test_python3_self_contained.bat for diagnostics")
        
        return 1
    
    finally:
        print("\n" + "=" * 60)
        input("Press Enter to exit...")

if __name__ == "__main__":
    sys.exit(main())