#!/usr/bin/env python3
"""
Manual UC Learn Scraper - Interactive version for Microsoft SSO

This version provides more manual interaction options to handle 
complex authentication flows like Microsoft SSO.
"""

import sys
import os
import time

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uc_learn_scraper import UCLearnScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ManualUCLearnScraper(UCLearnScraper):
    """Enhanced scraper with better manual interaction support."""
    
    def __init__(self, headless=False):
        """Initialize the scraper with dynamic course name support."""
        super().__init__(headless=headless)
        
        # Get course name from environment variable or default to MBAM601
        self.target_course = os.environ.get('TARGET_COURSE', 'MBAM601')
        print(f"🎯 Target course: {self.target_course}")
    
    def find_target_course(self):
        """Find the target course by name (replaces find_mbam601_course)."""
        print(f"Looking for {self.target_course} course in link text...")
        
        # Wait for page to load
        self.driver.implicitly_wait(10)
        
        # Try multiple XPath strategies to find the course
        xpath_strategies = [
            f"//a[contains(text(), '{self.target_course}')]",
            f"//a[starts-with(text(), '{self.target_course}')]",
            f"//a[contains(@title, '{self.target_course}')]",
            f"//span[contains(text(), '{self.target_course}')]/ancestor::a"
        ]
        
        course_links = []
        for xpath in xpath_strategies:
            try:
                links = self.driver.find_elements(By.XPATH, xpath)
                if links:
                    course_links.extend(links)
                    print(f"Found {len(links)} links using strategy: {xpath}")
            except Exception as e:
                print(f"XPath strategy failed {xpath}: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in course_links:
            link_id = id(link)
            if link_id not in seen:
                seen.add(link_id)
                unique_links.append(link)
        
        course_links = unique_links
        
        if not course_links:
            print(f"{self.target_course} course not found in any link text")
            return False
        
        print(f"Found {len(course_links)} potential {self.target_course} links")
        
        # Find the best match (prioritize course/view.php links)
        for i, link in enumerate(course_links):
            link_text = link.text.strip()
            link_url = link.get_attribute("href") or ""
            
            print(f"Checking link {i+1}: '{link_text}' -> {link_url}")
            
            # Check if this looks like a course link and contains our target course
            if (("course/view.php" in link_url or "course" in link_url.lower()) and 
                self.target_course in link_text):
                
                print(f"✅ Found exact {self.target_course} course link: '{link_text}'")
                print(f"Link URL: {link_url}")
                
                try:
                    # Click the course link
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    time.sleep(1)
                    link.click()
                    print(f"Successfully clicked {self.target_course} course link")
                    
                    # Wait for navigation and verify
                    time.sleep(3)
                    current_url = self.driver.current_url
                    print(f"Navigated to: {current_url}")
                    
                    if "course/view.php" in current_url:
                        print(f"✅ Successfully navigated to {self.target_course} course page!")
                        return True
                    else:
                        print(f"❌ Navigation failed - unexpected URL: {current_url}")
                        continue  # Try next link
                        
                except Exception as e:
                    print(f"Failed to click {self.target_course} link: {e}")
                    try:
                        self.driver.execute_script("arguments[0].click();", link)
                        print(f"Successfully clicked {self.target_course} link via JavaScript")
                        time.sleep(3)
                        current_url = self.driver.current_url
                        if "course/view.php" in current_url:
                            return True
                    except Exception as e2:
                        print(f"JavaScript click also failed: {e2}")
                        continue
        
        print(f"❌ Could not successfully navigate to {self.target_course} course")
        return False
        
        print(f"❌ Could not successfully navigate to {self.target_course} course")
        return False
    
    def get_course_filename(self, extension="json"):
        """Generate filename based on target course."""
        course_clean = self.target_course.lower().replace('-', '').replace(' ', '_')
        return f"{course_clean}_participants.{extension}"
    
    def save_results(self, filename: str = None):
        """Save results with dynamic filename based on course."""
        if filename is None:
            filename = self.get_course_filename("json")
        return super().save_results(filename)
    
    def display_in_browser(self, save_file=True):
        """Display results in browser with dynamic filename."""
        from datetime import datetime
        
        if not self.participants:
            print("No participants data to display.")
            return
        
        # Generate dynamic filename
        course_clean = self.target_course.lower().replace('-', '').replace(' ', '_')
        filename = f"{course_clean}_participants_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Use the parent class method but with our custom filename
        organized_data = self.organize_by_groups()
        if organized_data:
            html_content = self.generate_html_report()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML report saved to: {filename}")
            
            # Try to open in browser
            try:
                import webbrowser
                import os
                file_url = f"file://{os.path.abspath(filename)}"
                print(f"Browser URL: {file_url}")
                webbrowser.open(file_url)
            except Exception as e:
                print(f"Could not open browser: {e}")
        
        return filename
    
    def display_and_save_all_formats(self):
        """
        Display results in all available formats with dynamic course naming.
        """
        if not self.participants:
            print("No participants found to display.")
            return
        
        print("\n" + "="*60)
        print("DISPLAYING RESULTS IN ALL FORMATS")
        print("="*60)
        
        # 1. Console display
        print("📺 Console Display:")
        self.display_results()
        
        # 2. JSON save with dynamic filename
        print("\n💾 JSON Export:")
        json_filename = self.get_course_filename("json")
        self.save_results(json_filename)
        
        # 3. HTML browser display
        print("\n🌐 HTML Browser Display:")
        html_file = self.display_in_browser(save_file=True)
        
        print(f"\n✨ Results displayed in 3 formats:")
        print(f"   • Console output (above)")
        print(f"   • JSON file: {json_filename}")
        if html_file:
            print(f"   • HTML report: {os.path.basename(html_file)}")
            print(f"   • Opened in your default browser")
    
    def manual_login_flow(self) -> bool:
        """
        Manual login flow with user guidance.
        """
        try:
            print("🌐 Starting manual login flow...")
            print("=" * 50)
            
            # Navigate to UC Learn
            print("📱 Navigating to UC Learn...")
            self.driver.get(f"{self.base_url}/my/courses.php")
            
            # Wait and show current status
            time.sleep(3)
            current_url = self.driver.current_url
            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page title: {self.driver.title}")
            
            # Check if already logged in
            if "learn.canterbury.ac.nz" in current_url and "/my/" in current_url:
                print("✅ Already logged in!")
                return True
            
            # Guide user through login
            print("\n🔐 LOGIN INSTRUCTIONS:")
            print("=" * 30)
            if "microsoftonline.com" in current_url:
                print("🏢 Detected Microsoft SSO login page")
                print("📝 Please complete the following steps in the browser window:")
                print("   1. Enter your UC username (e.g., abc123@uclive.ac.nz)")
                print("   2. Click 'Next'")
                print("   3. Enter your password")
                print("   4. Click 'Sign in'")
                print("   5. Complete any additional authentication (MFA, etc.)")
            else:
                print("🔑 Please log in using the browser window")
            
            print("\n⏳ Waiting for you to complete login...")
            print("💡 Tip: Keep this terminal window visible to see progress updates")
            
            # Monitor login progress
            max_wait_time = 180  # 3 minutes
            start_time = time.time()
            check_interval = 2  # Check every 2 seconds
            
            while time.time() - start_time < max_wait_time:
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Check various success indicators
                if "learn.canterbury.ac.nz" in current_url:
                    if "/my/" in current_url or "dashboard" in current_url.lower():
                        print("🎉 Login successful! Redirected to UC Learn dashboard.")
                        return True
                    elif "/course/" in current_url:
                        print("🎉 Login successful! Redirected to a course page.")
                        # Navigate to courses page
                        self.driver.get(f"{self.base_url}/my/courses.php")
                        time.sleep(2)
                        return True
                
                # Provide periodic updates
                elapsed = int(time.time() - start_time)
                if elapsed % 15 == 0:  # Every 15 seconds
                    print(f"⏱️  Still waiting... ({elapsed}s elapsed)")
                    if "microsoftonline.com" in current_url:
                        print("   Still on Microsoft login page")
                    elif "canterbury.ac.nz" in current_url:
                        print("   On UC domain - almost there!")
                    else:
                        print(f"   Current domain: {current_url.split('/')[2] if '/' in current_url else current_url}")
                
                time.sleep(check_interval)
            
            # Timeout reached
            print("⏰ Login timeout reached.")
            current_url = self.driver.current_url
            
            if "canterbury.ac.nz" in current_url:
                print("🤔 You appear to be on a UC domain. Let's try to continue...")
                return True
            else:
                print("❌ Login was not completed in time.")
                print(f"📍 Current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Error during manual login: {str(e)}")
            return False
    
    def interactive_course_finding(self) -> str:
        """
        Interactive course finding with user assistance.
        """
        print(f"\n🔍 FINDING {self.target_course} COURSE:")
        print("=" * 30)
        
        try:
            # First, try automatic detection
            if self.find_target_course():
                print(f"✅ Automatic detection found and navigated to {self.target_course}!")
                return self.driver.current_url
            
            print(f"� Course {self.target_course} not found on this page.")
            print("❌ Scraping failed - target course not available.")
            
            # Manual search
            print("\n🔍 Please help find MBAM601:")
            print("   1. Look at the browser window")
            print("   2. Find the MBAM601 course")
            print("   3. RIGHT-CLICK on the course link")
            print("   4. Select 'Copy link address' or 'Copy link'")
            print("   5. Paste the URL here")
            
            while True:
                course_url = input("\n📎 Paste the MBAM601 course URL here (or 'quit' to exit): ").strip()
                
                if course_url.lower() == 'quit':
                    return None
                
                if 'course/view.php' in course_url and 'canterbury.ac.nz' in course_url:
                    print(f"✅ Valid course URL received: {course_url}")
                    
                    # Navigate to the provided URL
                    try:
                        self.driver.get(course_url)
                        time.sleep(3)
                        print("✅ Successfully navigated to the course page")
                        return course_url
                    except Exception as e:
                        print(f"❌ Error navigating to URL: {e}")
                        return None
                else:
                    print("❌ That doesn't look like a valid UC Learn course URL.")
                    print("   Make sure it contains 'course/view.php' and 'canterbury.ac.nz'")
                    
        except Exception as e:
            print(f"❌ Error finding course: {str(e)}")
            return None

    def scrape_course_participants(self) -> bool:
        """
        Main method to scrape course participants - callable from external scripts.
        Returns True if successful, False otherwise.
        """
        try:
            # Set up driver
            print("🚀 Setting up Chrome driver...")
            self.setup_driver()
            
            # Manual login
            if not self.manual_login_flow():
                print("❌ Login failed. Please try again.")
                return False
            
            # Find course with improved automatic detection
            if self.find_target_course():
                print(f"✅ Successfully found and navigated to {self.target_course} course!")
                course_url = self.driver.current_url
                print(f"Course URL: {course_url}")
            else:
                print(f"❌ Could not find {self.target_course} course.")
                print("❌ Scraping failed - target course not available.")
                return False
            
            # Navigate to participants
            print("\n👥 ACCESSING PARTICIPANTS:")
            print("=" * 30)
            if not self.navigate_to_participants(course_url):
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
            
            # Automatically save page source for debugging
            print("💡 Saving page source for debugging...")
            with open('participants_page_source.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("📄 Page source saved to participants_page_source.html")
            
            print("Extracting participant information...")
            participants = self.extract_participants()
            
            if not participants:
                print("❌ No participants found.")
                print("💡 The page structure might be different than expected.")
                print("🔍 Let's try some debugging...")
                
                # Show page title and URL for debugging
                print(f"📍 Current URL: {self.driver.current_url}")
                print(f"📄 Page title: {self.driver.title}")
                
                # Look for any tables on the page
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
                print(f"🔍 Found {len(tables)} tables on the page")
                
                if tables:
                    print("📋 Table contents preview:")
                    for i, table in enumerate(tables[:3]):  # Show first 3 tables
                        rows = table.find_elements(By.CSS_SELECTOR, "tr")
                        print(f"   Table {i+1}: {len(rows)} rows")
                        if rows:
                            first_row = rows[0].text.strip()
                            print(f"   First row: {first_row[:100]}...")
                
                return False
            
            # Display results in all formats
            print("\n🎯 RESULTS:")
            print("=" * 30)
            self.display_and_save_all_formats()
            
            print("\n✨ Scraping completed successfully!")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Scraping interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            return False
        finally:
            self.close()
            print("🔚 Browser closed.")


def main():
    """Main function for manual scraper."""
    # Get the target course name
    target_course = os.environ.get('TARGET_COURSE', 'MBAM601')
    
    print(f"🎓 UC Learn {target_course} Participant Scraper (Manual Mode)")
    print("=" * 60)
    print("This version provides step-by-step guidance for complex login flows.")
    print()
    
    # Initialize scraper
    scraper = ManualUCLearnScraper(headless=False)
    
    try:
        # Set up driver
        print("🚀 Setting up Chrome driver...")
        scraper.setup_driver()
        
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
        
        # Automatically save page source for debugging
        print("💡 Saving page source for debugging...")
        with open('participants_page_source.html', 'w', encoding='utf-8') as f:
            f.write(scraper.driver.page_source)
        print("📄 Page source saved to participants_page_source.html")
        
        print("Extracting participant information...")
        participants = scraper.extract_participants()
        
        if not participants:
            print("❌ No participants found.")
            print("💡 The page structure might be different than expected.")
            print("🔍 Let's try some debugging...")
            
            # Show page title and URL for debugging
            print(f"📍 Current URL: {scraper.driver.current_url}")
            print(f"📄 Page title: {scraper.driver.title}")
            
            # Look for any tables on the page
            tables = scraper.driver.find_elements(By.CSS_SELECTOR, "table")
            print(f"🔍 Found {len(tables)} tables on the page")
            
            if tables:
                print("📋 Table contents preview:")
                for i, table in enumerate(tables[:3]):  # Show first 3 tables
                    rows = table.find_elements(By.CSS_SELECTOR, "tr")
                    print(f"   Table {i+1}: {len(rows)} rows")
                    if rows:
                        first_row = rows[0].text.strip()
                        print(f"   First row: {first_row[:100]}...")
            
            return
        
        # Display results in all formats
        print("\n🎯 RESULTS:")
        print("=" * 30)
        scraper.display_and_save_all_formats()
        
        print("\n✨ Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
    finally:
        scraper.close()
        print("🔚 Browser closed. Goodbye!")


if __name__ == "__main__":
    main()