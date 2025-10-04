#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable UC Learn Scraper
Windows-compatible version with bundled drivers
"""

from pathlib import Path
import os
import sys
import time
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests

class PortableUCLearnScraper:
    """Portable version of UC Learn scraper with bundled drivers."""
    
    def __init__(self, headless=False, portable_dir=None, temp_dir=None):
        """Initialize the portable scraper."""
        self.headless = headless
        self.driver = None
        self.portable_dir = Path(portable_dir) if portable_dir else Path(__file__).parent
        
        # Set up temp directory
        if temp_dir:
            self.temp_dir = Path(temp_dir)
        else:
            self.temp_dir = Path(tempfile.gettempdir()) / "uc_scraper_portable"
        
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Get course name from environment variable or default to MBAM601
        self.target_course = os.environ.get('TARGET_COURSE', 'MBAM601')
        print("Target course: " + self.target_course)

import sys
import os
import time
import tempfile
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manual_scraper import ManualUCLearnScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class PortableUCLearnScraper(ManualUCLearnScraper):
    """Enhanced scraper that works without admin rights and with bundled drivers."""
    
    def __init__(self, headless=False, portable_dir=None, temp_dir=None):
        """Initialize the portable scraper."""
        # Don't call super().__init__ yet - we need to set up portable environment first
        self.headless = headless
        self.portable_dir = Path(portable_dir) if portable_dir else Path(__file__).parent
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "uc_learn_scraper"
        
        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Get course name from environment variable or default to MBAM601
        self.target_course = os.environ.get('TARGET_COURSE', 'MBAM601')
        print(f"🎯 Target course: {self.target_course}")
        
        # Set up portable paths
        self.setup_portable_paths()
        
        # Initialize base class variables
        self.base_url = "https://learn.canterbury.ac.nz"
        self.participants = []
        self.driver = None
    
    def setup_portable_paths(self):
        """Set up paths for portable operation."""
        print("🔧 Setting up portable environment...")
        
        # Find bundled drivers
        self.chrome_driver_path = None
        self.firefox_driver_path = None
        
        # Check for bundled drivers in the executable directory
        if getattr(sys, 'frozen', False):
            # Running as executable - drivers should be in _MEIPASS
            bundle_dir = Path(sys._MEIPASS)
        else:
            # Running as script - drivers should be in drivers subfolder
            bundle_dir = self.portable_dir
        
        # Look for Chrome driver
        for chrome_name in ['chromedriver.exe', 'chromedriver']:
            # First check current directory (flattened package)
            chrome_path = bundle_dir / chrome_name
            if chrome_path.exists():
                self.chrome_driver_path = str(chrome_path)
                print(f"✅ Found bundled ChromeDriver: {chrome_path}")
                break
            # Fallback: check drivers subdirectory
            chrome_path = bundle_dir / 'drivers' / chrome_name
            if chrome_path.exists():
                self.chrome_driver_path = str(chrome_path)
                print(f"✅ Found bundled ChromeDriver: {chrome_path}")
                break
        
        # Look for Firefox driver
        for firefox_name in ['geckodriver.exe', 'geckodriver']:
            # First check current directory (flattened package)
            firefox_path = bundle_dir / firefox_name
            if firefox_path.exists():
                self.firefox_driver_path = str(firefox_path)
                print(f"✅ Found bundled GeckoDriver: {firefox_path}")
                break
            # Fallback: check drivers subdirectory
            firefox_path = bundle_dir / 'drivers' / firefox_name
            if firefox_path.exists():
                self.firefox_driver_path = str(firefox_path)
                print(f"✅ Found bundled GeckoDriver: {firefox_path}")
                break
        
        # Set up user data directories in temp space (no admin needed)
        self.chrome_user_data = self.temp_dir / "chrome_data"
        self.firefox_profile_dir = self.temp_dir / "firefox_profile"
        
        self.chrome_user_data.mkdir(exist_ok=True)
        self.firefox_profile_dir.mkdir(exist_ok=True)
        
        print(f"📁 Chrome data dir: {self.chrome_user_data}")
        print(f"📁 Firefox profile dir: {self.firefox_profile_dir}")
    
    def setup_driver(self):
        """Set up browser driver with portable configuration."""
        print("🚀 Setting up portable browser driver...")
        
        # Try Chrome first (more reliable)
        if self.chrome_driver_path and self.setup_chrome_driver():
            return True
        
        # Fall back to Firefox
        if self.firefox_driver_path and self.setup_firefox_driver():
            return True
        
        # Last resort: try system drivers
        print("⚠️ Bundled drivers not found, trying system drivers...")
        return self.setup_system_drivers()
    
    def setup_chrome_driver(self):
        """Set up Chrome with portable configuration."""
        try:
            print("🔧 Setting up portable Chrome driver...")
            
            # Chrome options for portable operation
            chrome_options = ChromeOptions()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Portable Chrome configuration (no admin rights needed)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Faster loading
            chrome_options.add_argument("--disable-javascript")  # Not needed for basic scraping
            
            # Use portable user data directory
            chrome_options.add_argument(f"--user-data-dir={self.chrome_user_data}")
            
            # Window size for consistent behavior
            chrome_options.add_argument("--window-size=1280,720")
            
            # Try bundled driver first
            try:
                service = ChromeService(executable_path=self.chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Portable Chrome driver initialized successfully!")
                return True
            except Exception as bundled_error:
                print(f"⚠️ Bundled ChromeDriver failed: {bundled_error}")
                print("🔄 Trying webdriver-manager for automatic driver download...")
                
                # Fallback to webdriver-manager for automatic driver download
                from webdriver_manager.chrome import ChromeDriverManager
                
                # Download the correct driver version automatically
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ Auto-downloaded Chrome driver initialized successfully!")
                return True
            
        except Exception as e:
            print(f"❌ Failed to set up portable Chrome driver: {e}")
            return False
    
    def setup_firefox_driver(self):
        """Set up Firefox with portable configuration."""
        try:
            print("🔧 Setting up portable Firefox driver...")
            
            # Firefox options for portable operation
            firefox_options = FirefoxOptions()
            
            if self.headless:
                firefox_options.add_argument("--headless")
            
            # Common Firefox binary locations on Windows
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                r"C:\Users\%s\AppData\Local\Mozilla Firefox\firefox.exe" % os.environ.get('USERNAME', ''),
            ]
            
            # Find Firefox binary
            firefox_binary = None
            for path in firefox_paths:
                if os.path.exists(path):
                    firefox_binary = path
                    break
            
            if firefox_binary:
                firefox_options.binary_location = firefox_binary
                print(f"✅ Found Firefox binary: {firefox_binary}")
            else:
                print("⚠️ Firefox binary not found in common locations")
            
            # Portable Firefox configuration
            firefox_options.set_preference("browser.cache.disk.enable", False)
            firefox_options.set_preference("browser.cache.memory.enable", False)
            firefox_options.set_preference("browser.download.folderList", 2)
            firefox_options.set_preference("browser.download.dir", str(self.temp_dir))
            
            # Set profile directory using options (modern approach)
            firefox_options.add_argument(f"--profile={self.firefox_profile_dir}")
            
            # Try bundled driver first, then webdriver-manager
            try:
                service = FirefoxService(executable_path=self.firefox_driver_path)
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                print("✅ Portable Firefox driver initialized successfully!")
                return True
            except Exception as bundled_error:
                print(f"⚠️ Bundled FirefoxDriver failed: {bundled_error}")
                print("🔄 Trying webdriver-manager for automatic driver download...")
                
                from webdriver_manager.firefox import GeckoDriverManager
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                print("✅ Auto-downloaded Firefox driver initialized successfully!")
                return True
            
        except Exception as e:
            print(f"❌ Failed to set up portable Firefox driver: {e}")
            return False
    
    def setup_system_drivers(self):
        """Fallback to system drivers using webdriver-manager."""
        try:
            print("🔄 Trying system drivers as fallback...")
            
            # Use the parent class method as fallback
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.firefox import GeckoDriverManager
            
            # Try Chrome first
            try:
                chrome_options = ChromeOptions()
                if self.headless:
                    chrome_options.add_argument("--headless")
                
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(f"--user-data-dir={self.chrome_user_data}")
                
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ System Chrome driver initialized!")
                return True
                
            except Exception as e:
                print(f"System Chrome failed: {e}")
            
            # Try Firefox
            try:
                firefox_options = FirefoxOptions()
                if self.headless:
                    firefox_options.add_argument("--headless")
                
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                print("✅ System Firefox driver initialized!")
                return True
                
            except Exception as e:
                print(f"System Firefox failed: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ All driver setup methods failed: {e}")
            return False
    
    def save_results(self, filename: str = None):
        """Save results in current working directory (where user ran the executable)."""
        if filename is None:
            filename = self.get_course_filename("json")
        
        # Save in current working directory, not in temp or app directory
        output_path = Path.cwd() / filename
        
        if self.participants:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.participants, f, indent=2, ensure_ascii=False)
            print(f"💾 JSON data saved to: {output_path}")
            return str(output_path)
        else:
            print("No participants data to save.")
            return None
    
    def display_in_browser(self, save_file=True):
        """Display results in browser with file saved to current directory."""
        from datetime import datetime
        
        if not self.participants:
            print("No participants data to display.")
            return
        
        # Generate dynamic filename in current working directory
        course_clean = self.target_course.lower().replace('-', '').replace(' ', '_')
        filename = f"{course_clean}_participants_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = Path.cwd() / filename
        
        # Use the parent class method but save to current directory
        organized_data = self.organize_by_groups()
        if organized_data:
            html_content = self.generate_html_report()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 HTML report saved to: {output_path}")
            
            # Try to open in browser
            try:
                import webbrowser
                file_url = f"file://{output_path.absolute()}"
                print(f"🌐 Opening in browser: {file_url}")
                webbrowser.open(file_url)
            except Exception as e:
                print(f"Could not open browser: {e}")
        
        return str(output_path)
    
    def cleanup_temp_files(self):
        """Clean up temporary files (optional - Windows will clean temp on reboot)."""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print(f"🧹 Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            print(f"Note: Could not clean temp files: {e} (this is OK)")
    
    def close(self):
        """Close browser and clean up."""
        if self.driver:
            try:
                self.driver.quit()
                print("🔚 Browser closed.")
            except Exception as e:
                print(f"Note: Error closing browser: {e}")
        
        # Optionally clean up temp files
        # self.cleanup_temp_files()  # Commented out - let Windows handle temp cleanup


def main():
    """Main function for portable scraper."""
    # Get the target course name
    target_course = os.environ.get('TARGET_COURSE', 'MBAM601')
    
    print(f"🎓 UC Learn {target_course} Participant Scraper (Portable Mode)")
    print("=" * 65)
    print("This version is completely self-contained and requires no admin rights.")
    print()
    
    # Initialize portable scraper
    scraper = PortableUCLearnScraper(headless=False)
    
    try:
        # Set up driver
        print("🚀 Setting up portable browser driver...")
        if not scraper.setup_driver():
            print("❌ Failed to set up any browser driver.")
            return
        
        # Manual login
        if not scraper.manual_login_flow():
            print("❌ Login failed. Please try again.")
            return
        
        # Find course with improved automatic detection
        if scraper.find_target_course():
            print(f"✅ Successfully found and navigated to {target_course} course!")
            course_url = scraper.driver.current_url
            print(f"Course URL: {course_url}")
        else:
            print(f"❌ Could not find {target_course} course.")
            print("❌ Scraping failed - target course not available.")
            return
        
        # Navigate to participants
        print("\n👥 ACCESSING PARTICIPANTS:")
        print("=" * 30)
        if not scraper.navigate_to_participants(course_url):
            print("❌ Could not access participants page.")
            print("💡 You might not have permission or the page structure has changed.")
            
            # Offer manual navigation
            print("\n🔧 Manual option:")
            print("   1. Navigate to the participants page manually in the browser")
            print("   2. Come back here and press Enter")
            input("Press Enter when you're on the participants page...")
        
        # Extract participants
        print("\n📊 EXTRACTING PARTICIPANT DATA:")
        print("=" * 30)
        
        print("Extracting participant information...")
        participants = scraper.extract_participants()
        
        if not participants:
            print("❌ No participants found.")
            return
        
        # Display results in all formats (saves to current directory)
        print("\n🎯 RESULTS:")
        print("=" * 30)
        scraper.display_and_save_all_formats()
        
        print("\n✨ Scraping completed successfully!")
        print("📁 Files saved in current directory (where you ran the executable)")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
    finally:
        scraper.close()
        print("🔚 Portable scraper finished.")


if __name__ == "__main__":
    main()