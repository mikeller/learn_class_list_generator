#!/usr/bin/env python3
"""
UC Learn MBAM601 Participant Scraper

This script logs into UC Learn and extracts the participant list for MBAM601,
organizing them by groups and displaying the results in a clean format.
"""

import os
import time
import sys
from collections import defaultdict
from typing import List, Dict, Optional
import json
import webbrowser
import tempfile
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class UCLearnScraper:
    """Scraper for UC Learn to extract MBAM601 participant information."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize the scraper with Chrome driver.
        
        Args:
            headless: Whether to run browser in headless mode
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.base_url = "https://learn.canterbury.ac.nz"
        self.participants = []
        
    def setup_driver(self):
        """Set up Chrome driver with appropriate options."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Add other useful options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        
        print("Chrome driver initialized successfully")
    
    def login(self, username: str, password: str) -> bool:
        """
        Log into UC Learn.
        
        Args:
            username: UC Learn username
            password: UC Learn password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            print("Navigating to UC Learn...")
            self.driver.get(f"{self.base_url}/my/courses.php")
            
            # Give some time for page to load and print current URL
            time.sleep(3)
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Wait for login page or check if already logged in
            try:
                # Check if we're already on the courses page
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "course-info-container")))
                print("Already logged in!")
                return True
            except TimeoutException:
                print("Not logged in yet, looking for login form...")
            
            # Look for login form - try different approaches
            print("Looking for login form...")
            
            # Try to find username field with different selectors
            username_selectors = [
                "input[name='username']",
                "input[id='username']", 
                "input[type='text']",
                "input[name='user']",
                "input[name='email']"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"Found username field with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not username_field:
                print("Could not find username field. Page might need manual interaction.")
                print("Please log in manually in the browser window, then press Enter here to continue...")
                input("Press Enter after you've logged in manually...")
                
                # Check if we're now on the courses page
                try:
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "course-info-container")))
                    print("Manual login successful!")
                    return True
                except TimeoutException:
                    print("Still not on courses page after manual login.")
                    return False
            
            # Try to find password field - Microsoft SSO might load it dynamically
            password_selectors = [
                "input[name='passwd']",  # Microsoft SSO uses 'passwd'
                "input[name='password']",
                "input[id='passwordInput']",
                "input[id='i0118']",  # Microsoft's password field ID
                "input[type='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"Found password field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                print("Password field not visible yet. This might be Microsoft SSO.")
                print("Entering username first to proceed to password step...")
                
                # Enter username and proceed
                username_field.clear()
                username_field.send_keys(username)
                
                # Look for "Next" button
                next_selectors = [
                    "input[type='submit']",
                    "input[value='Next']",
                    "button[type='submit']",
                    "#idSIButton9",  # Microsoft's Next button ID
                    ".btn-primary"
                ]
                
                next_button = None
                for selector in next_selectors:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"Found Next button with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue
                
                if next_button:
                    next_button.click()
                    print("Clicked Next button, waiting for password field...")
                    
                    # Wait for password field to appear
                    try:
                        password_field = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='passwd'], input[type='password']"))
                        )
                        print("Password field appeared!")
                    except TimeoutException:
                        print("Password field didn't appear. You may need to complete authentication manually.")
                        print("Please complete the login process in the browser, then press Enter here...")
                        input("Press Enter after completing login...")
                        
                        # Check if login succeeded
                        if "learn.canterbury.ac.nz" in self.driver.current_url or "canterbury.ac.nz" in self.driver.current_url:
                            print("Detected UC Learn domain. Assuming login succeeded.")
                            return True
                        else:
                            return False
                else:
                    print("Could not find Next button.")
                    return False
            
            # If we have both username and password fields, proceed with login
            if password_field:
                print("Entering credentials...")
                if username_field.get_attribute('value') == '':  # Username not entered yet
                    username_field.clear()
                    username_field.send_keys(username)
                
                password_field.clear()
                password_field.send_keys(password)
                
                # Find and click login button
                login_selectors = [
                    "input[type='submit']",
                    "button[type='submit']",
                    "input[value*='Sign in']",
                    "button:contains('Sign in')",
                    "#idSIButton9",  # Microsoft's Sign in button
                    ".btn-primary",
                    ".login-btn"
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        if "contains" in selector:
                            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
                        else:
                            login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"Found login button with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue
                
                if login_button:
                    login_button.click()
                    print("Clicked login button...")
                else:
                    print("Could not find login button. You may need to click it manually.")
                    print("Please click the Sign In button in the browser, then press Enter here...")
                    input("Press Enter after clicking Sign In...")
            
            # Wait for successful login and redirect back to UC Learn
            print("Waiting for login to complete and redirect to UC Learn...")
            max_wait_time = 30  # Wait up to 30 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                current_url = self.driver.current_url
                if "learn.canterbury.ac.nz" in current_url:
                    print(f"Redirected back to UC Learn: {current_url}")
                    
                    # Check for course page elements
                    try:
                        # Try different selectors for UC Learn course page
                        course_selectors = [
                            ".course-info-container",
                            ".coursebox",
                            ".course-listitem",
                            "#page-my-index",
                            ".dashboard",
                            "[data-region='content']"
                        ]
                        
                        for selector in course_selectors:
                            try:
                                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                print(f"Found course page element: {selector}")
                                print("Login successful!")
                                return True
                            except NoSuchElementException:
                                continue
                        
                        # If no specific elements found but we're on UC Learn, assume success
                        print("On UC Learn domain but page structure might be different.")
                        print("Assuming login successful.")
                        return True
                        
                    except Exception as e:
                        print(f"Checking course page: {e}")
                
                time.sleep(1)
            
            print("Login timeout. You may need to complete authentication manually.")
            print("Current URL:", self.driver.current_url)
            if "learn.canterbury.ac.nz" in self.driver.current_url:
                return True
            else:
                return False
            
        except TimeoutException:
            print("Login failed: Timeout waiting for page elements")
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    
    def find_mbam601_course(self) -> Optional[str]:
        """
        Find and navigate to the MBAM601 course by following any link with MBAM601 in the text.
        
        Returns:
            Course URL if found, None otherwise
        """
        try:
            print("Looking for MBAM601 course in link text...")
            
            # Get all links on the page
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a")
            
            for link in all_links:
                link_text = link.text.strip()
                link_title = link.get_attribute("title") or ""
                href = link.get_attribute("href") or ""
                
                # Check if MBAM601 appears in the visible text or title of the link
                if "MBAM601" in link_text or "MBAM601" in link_title:
                    print(f"Found MBAM601 course link: '{link_text}'")
                    print(f"Link URL: {href}")
                    
                    # Click the link to navigate to the course
                    try:
                        # Scroll to the link to make sure it's visible
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
                        time.sleep(1)
                        
                        # Try clicking the link
                        link.click()
                        print("Successfully clicked MBAM601 course link")
                        
                        # Wait for the course page to load
                        time.sleep(3)
                        
                        # Get the current URL after navigation
                        current_url = self.driver.current_url
                        print(f"Navigated to: {current_url}")
                        
                        # Verify we're on a course page
                        if "course/view.php" in current_url or "course" in current_url:
                            return current_url
                        else:
                            print(f"Link didn't lead to a course page: {current_url}")
                            continue
                            
                    except Exception as e:
                        print(f"Error clicking link '{link_text}': {str(e)}")
                        # Try using JavaScript click as fallback
                        try:
                            self.driver.execute_script("arguments[0].click();", link)
                            print("Successfully clicked using JavaScript")
                            time.sleep(3)
                            current_url = self.driver.current_url
                            if "course/view.php" in current_url or "course" in current_url:
                                return current_url
                        except:
                            print("JavaScript click also failed")
                            continue
            
            print("MBAM601 course not found in any link text")
            return None
            
        except Exception as e:
            print(f"Error finding MBAM601 course: {str(e)}")
            return None
    
    def navigate_to_participants(self, course_url: str) -> bool:
        """
        Navigate to the participants page of the course by finding 'Participants' link text.
        Since find_mbam601_course now navigates directly, course_url may be current URL.
        
        Args:
            course_url: URL of the MBAM601 course (may be current page)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if we're already on the course page
            current_url = self.driver.current_url
            if "course/view.php" not in current_url and course_url:
                print("Navigating to course page...")
                self.driver.get(course_url)
                time.sleep(3)
            else:
                print("Already on course page, looking for participants...")
            
            # Wait for course page to load
            time.sleep(2)
            
            # Look for participants link by text content with multiple strategies
            print("Looking for 'Participants' link...")
            
            participants_link = None
            
            # Strategy 1: Direct text search in all links
            all_links = self.driver.find_elements(By.CSS_SELECTOR, "a")
            
            for link in all_links:
                link_text = link.text.strip().lower()
                link_title = (link.get_attribute("title") or "").lower()
                
                # Look for "participants" in the link text or title
                if "participants" in link_text or "participants" in link_title:
                    participants_link = link
                    print(f"Found participants link: '{link.text.strip()}'")
                    break
            
            # Strategy 2: XPath search for case-insensitive "Participants"
            if not participants_link:
                print("Trying XPath search for 'Participants'...")
                try:
                    participants_link = self.driver.find_element(
                        By.XPATH, "//a[contains(translate(text(), 'PARTICIPANTS', 'participants'), 'participants')]"
                    )
                    print(f"Found participants link via XPath: '{participants_link.text.strip()}'")
                except:
                    pass
            
            # Strategy 3: Look in navigation menus, sidebars, and course sections
            if not participants_link:
                print("Looking in navigation menus and course sections...")
                nav_selectors = [
                    "nav a", ".nav a", ".navigation a", ".sidebar a", ".menu a", 
                    ".block a", ".course-content a", ".activity a", ".section a",
                    ".page-header a", ".page-content a", "[role='navigation'] a"
                ]
                
                for selector in nav_selectors:
                    try:
                        nav_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for nav_link in nav_links:
                            nav_text = nav_link.text.strip().lower()
                            if "participants" in nav_text:
                                participants_link = nav_link
                                print(f"Found participants link in {selector}: '{nav_link.text.strip()}'")
                                break
                        if participants_link:
                            break
                    except:
                        continue
            
            # Strategy 4: Look for user/index.php links which are typically participants pages
            if not participants_link:
                print("Looking for user/index.php links...")
                user_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='user/index.php']")
                if user_links:
                    participants_link = user_links[0]
                    print(f"Found user/index.php link: '{participants_link.text.strip()}'")
            
            if participants_link:
                # Multiple click strategies
                success = False
                
                # Strategy 1: Regular click
                try:
                    # Scroll to the link to ensure it's visible
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", participants_link)
                    time.sleep(1)
                    
                    # Wait for element to be clickable
                    wait = WebDriverWait(self.driver, 10)
                    clickable_link = wait.until(EC.element_to_be_clickable(participants_link))
                    clickable_link.click()
                    success = True
                    print("Successfully clicked participants link")
                    
                except Exception as e:
                    print(f"Regular click failed: {str(e)}")
                
                # Strategy 2: JavaScript click
                if not success:
                    try:
                        self.driver.execute_script("arguments[0].click();", participants_link)
                        success = True
                        print("Successfully clicked participants link using JavaScript")
                    except Exception as e:
                        print(f"JavaScript click failed: {str(e)}")
                
                # Strategy 3: Navigate to href directly
                if not success:
                    try:
                        href = participants_link.get_attribute("href")
                        if href:
                            print(f"Navigating directly to: {href}")
                            self.driver.get(href)
                            success = True
                    except Exception as e:
                        print(f"Direct navigation failed: {str(e)}")
                
                if success:
                    # Wait for participants page to load
                    print("Waiting for participants page to load...")
                    time.sleep(5)  # Give more time for page load
                    
                    # Check if we're on the participants page
                    current_url = self.driver.current_url
                    page_title = self.driver.title.lower()
                    
                    if ("user/index.php" in current_url or 
                        "participants" in current_url.lower() or 
                        "participants" in page_title):
                        print("Successfully navigated to participants page")
                        return True
                    else:
                        print(f"May have navigated to participants page. Current URL: {current_url}")
                        print(f"Page title: {page_title}")
                        # Try to proceed anyway - sometimes the URL doesn't match expected patterns
                        return True
                else:
                    print("All click strategies failed")
                    return False
            else:
                print("Could not find 'Participants' link anywhere on the page")
                
                # Debug: Print some page information
                print("Page title:", self.driver.title)
                print("Current URL:", self.driver.current_url)
                
                # Look for any links that might be participants-related
                print("Looking for any user-related links...")
                possible_links = self.driver.find_elements(By.CSS_SELECTOR, "a")
                user_related = []
                for link in possible_links:
                    text = link.text.strip().lower()
                    href = link.get_attribute("href") or ""
                    if any(word in text for word in ["user", "people", "member", "student"]) or "user" in href:
                        user_related.append((text, href))
                
                if user_related:
                    print("Found these user-related links:")
                    for text, href in user_related[:5]:
                        print(f"  - '{text}' -> {href}")
                
                return False
                
        except Exception as e:
            print(f"Error navigating to participants: {str(e)}")
            return False
    
    def extract_participants(self) -> List[Dict]:
        """
        Extract participant information from the participants page, handling pagination.
        
        Returns:
            List of participant dictionaries
        """
        try:
            print("Extracting participant information...")
            
            all_participants = []
            page_number = 1
            max_pages = 20  # Safety limit to prevent infinite loops
            
            while page_number <= max_pages:
                print(f"Processing page {page_number}...")
                
                # Wait for page to fully load
                time.sleep(3)
                
                page_participants = self.extract_participants_from_current_page()
                
                if page_participants:
                    print(f"Found {len(page_participants)} participants on page {page_number}")
                    all_participants.extend(page_participants)
                else:
                    print(f"No participants found on page {page_number}")
                
                # Look for next page link - only numbered pagination (1, 2, 3, ...)
                next_page_found = False
                next_page_num = page_number + 1
                print(f"Looking for page {next_page_num} link...")
                
                # Use XPath to find numbered pagination links only
                xpath_selectors = [
                    f"//li[@data-page-number='{next_page_num}']//a[@class='page-link']",
                    f"//li[@class='page-item ' and @data-page-number='{next_page_num}']//a",
                    f"//a[contains(@class, 'page-link') and .//span[text()='{next_page_num}']]",
                    f"//ul[contains(@class, 'pagination')]//a[.//span[text()='{next_page_num}']]",
                    f"//nav[contains(@class, 'pagination')]//a[contains(text(), '{next_page_num}')]"
                ]
                
                for xpath_selector in xpath_selectors:
                    try:
                        next_link = self.driver.find_element(By.XPATH, xpath_selector)
                        
                        # Verify it's actually a clickable pagination link
                        href = next_link.get_attribute("href") or ""
                        if next_link.is_enabled() and next_link.is_displayed() and href and href != "#":
                            print(f"Found page {next_page_num} link: '{next_link.text.strip()}'")
                            print(f"Link href: {href}")
                            
                            # Scroll to the link and click it
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_link)
                            time.sleep(1)
                            
                            try:
                                next_link.click()
                                print(f"Successfully clicked page {next_page_num} link")
                                next_page_found = True
                                page_number += 1
                                # Wait for the new page to load
                                time.sleep(2)
                                break
                            except Exception as e:
                                print(f"Click failed, trying JavaScript click: {e}")
                                self.driver.execute_script("arguments[0].click();", next_link)
                                print(f"Successfully clicked page {next_page_num} link via JavaScript")
                                next_page_found = True
                                page_number += 1
                                # Wait for the new page to load
                                time.sleep(2)
                                break
                            
                    except Exception as ex:
                        print(f"XPath selector failed: {xpath_selector} - {ex}")
                        continue
                
                # If no numbered pagination found, we're done
                if not next_page_found:
                    print(f"No more pages found. Finished processing {page_number} page(s)")
                    break
                
                # If no pagination found at all, we're done
                if not next_page_found:
                    print(f"No more pages found. Finished processing {page_number} page(s)")
                    break
            
            # Remove duplicates based on name
            seen_names = set()
            unique_participants = []
            
            for participant in all_participants:
                name = participant["name"]
                if name not in seen_names and len(name) > 2:
                    seen_names.add(name)
                    unique_participants.append(participant)
            
            print(f"Total extracted: {len(all_participants)} participants")
            print(f"Unique participants: {len(unique_participants)} (after removing duplicates)")
            
            # Debug: Print first few participants
            if unique_participants:
                print("Sample participants found:")
                for i, p in enumerate(unique_participants[:5]):
                    print(f"  {i+1}. Name: '{p['name']}', Group: '{p.get('group', 'Unknown')}', Role: '{p.get('role', 'Unknown')}'")
            
            self.participants = unique_participants
            return unique_participants
            
        except Exception as e:
            print(f"Error extracting participants: {str(e)}")
            return []
    
    def extract_participants_from_current_page(self) -> List[Dict]:
        """
        Extract participants from the current page only.
        
        Returns:
            List of participant dictionaries from current page
        """
        try:
            participants = []
            
            # Print page source length for debugging
            if len(self.driver.page_source) > 0:
                print(f"Page loaded successfully, content length: {len(self.driver.page_source)}")
            
            # Try different approaches to find participants on current page
            
            # Approach 1: Look for user cards or user info containers
            user_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".user-info, .user-card, .participant, .user, [data-region='user']")
            
            if user_elements:
                print(f"Found {len(user_elements)} user elements")
                for element in user_elements:
                    participant = self.extract_participant_from_element(element)
                    if participant and participant["name"]:
                        participants.append(participant)
            
            # Approach 2: Look for table rows (most common in UC Learn)
            if not participants:
                print("Looking for table-based participant list...")
                tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
                
                for table in tables:
                    rows = table.find_elements(By.CSS_SELECTOR, "tr")
                    
                    if len(rows) > 1:  # Skip tables with no data
                        print(f"Found table with {len(rows)} rows")
                        
                        # Skip header row(s) - look for actual participant data
                        for i, row in enumerate(rows):
                            row_text = row.text.strip()
                            
                            # Skip obvious header rows
                            if i == 0 and any(header in row_text.lower() for header in 
                                            ['name', 'user', 'participant', 'student', 'email']):
                                continue
                            
                            # Skip empty rows
                            if not row_text or len(row_text) < 3:
                                continue
                            
                            participant = self.extract_participant_from_row(row)
                            if participant and participant["name"] and len(participant["name"]) > 2:
                                participants.append(participant)
            
            # Approach 3: Look for list items
            if not participants:
                print("Looking for list-based participant display...")
                list_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".user-list, .participants, .userlist, ul li, ol li")
                
                if list_containers:
                    print(f"Found {len(list_containers)} list items")
                    for item in list_containers:
                        participant = self.extract_participant_from_element(item)
                        if participant and participant["name"]:
                            participants.append(participant)
            
            # Approach 4: Look for any div containing user information
            if not participants:
                print("Looking for div-based user information...")
                divs = self.driver.find_elements(By.CSS_SELECTOR, "div")
                
                potential_user_divs = []
                for div in divs:
                    div_text = div.text.strip()
                    # Look for divs that might contain user names
                    if (len(div_text) > 5 and len(div_text) < 200 and 
                        any(indicator in div_text.lower() for indicator in 
                            ['@', 'group', 'student', 'select']) and
                        not any(skip in div_text.lower() for skip in 
                               ['menu', 'navigation', 'header', 'footer', 'button'])):
                        potential_user_divs.append(div)
                
                if potential_user_divs:
                    print(f"Found {len(potential_user_divs)} potential user divs")
                    for div in potential_user_divs[:50]:  # Limit to avoid too much processing
                        participant = self.extract_participant_from_element(div)
                        if participant and participant["name"] and len(participant["name"]) > 2:
                            participants.append(participant)
            
            return participants
            
        except Exception as e:
            print(f"Error extracting participants from current page: {str(e)}")
            return []
    
    def extract_participant_from_element(self, element) -> Optional[Dict]:
        """Extract participant info from a web element."""
        try:
            text = element.text.strip()
            if not text or len(text) < 3:
                return None
            
            # Try to find name and group information
            name = ""
            group = "Unknown"
            role = "Unknown"
            
            # Look for name in various elements
            name_elements = element.find_elements(By.CSS_SELECTOR, ".fullname, .username, .user-name, a")
            if name_elements:
                name = name_elements[0].text.strip()
            else:
                # Fallback to element text
                lines = text.split('\n')
                name = lines[0].strip() if lines else text
            
            # Clean up name - remove "Select '" prefix if present
            if name.startswith("Select '") and name.endswith("'"):
                name = name[8:-1]  # Remove "Select '" from start and "'" from end
            
            # Look for group information in the text
            text_lines = text.split('\n')
            for line in text_lines:
                line_lower = line.lower().strip()
                
                # Look for Group patterns (Group A, Group B, etc.)
                if 'group' in line_lower and any(letter in line_lower for letter in 'abcdefghijklmnopqrstuvwxyz'):
                    group = line.strip()
                    break
                
                # Look for role information
                if any(role_keyword in line_lower for role_keyword in 
                       ['student', 'lecturer', 'coordinator', 'administrator', 'tutor', 'teaching assistant']):
                    role = line.strip()
            
            return {
                "name": name,
                "group": group,
                "role": role,
                "raw_text": text
            }
            
        except Exception as e:
            print(f"Error extracting from element: {str(e)}")
            return None
    
    def extract_participant_from_row(self, row) -> Optional[Dict]:
        """Extract participant info from a table row."""
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 1:
                return None
            
            name = ""
            group = "Unknown"
            role = "Unknown"
            
            # Extract information from table cells
            for i, cell in enumerate(cells):
                cell_text = cell.text.strip()
                
                if i == 0:  # First cell usually contains name
                    # Clean up name - remove "Select '" prefix if present
                    if cell_text.startswith("Select '") and cell_text.endswith("'"):
                        name = cell_text[8:-1]
                    else:
                        name = cell_text
                elif "group" in cell_text.lower():
                    group = cell_text
                elif any(role_keyword in cell_text.lower() for role_keyword in 
                        ['student', 'lecturer', 'coordinator', 'administrator', 'tutor']):
                    role = cell_text
            
            # If we don't have a good name, skip this entry
            if not name or len(name) < 3 or name in ["Select", "'"]:
                return None
            
            # Try to extract group information from the entire row text
            row_text = row.text.strip()
            if group == "Unknown" and row_text:
                lines = row_text.split('\n')
                for line in lines:
                    line_lower = line.lower().strip()
                    if 'group' in line_lower and len(line.strip()) < 20:  # Likely a group identifier
                        group = line.strip()
                        break
            
            return {
                "name": name,
                "group": group,
                "role": role,
                "raw_text": row_text
            }
            
        except Exception as e:
            print(f"Error extracting from row: {str(e)}")
            return None
    
    def organize_by_groups(self) -> Dict[str, List[str]]:
        """
        Organize participants by their groups, prioritizing actual study groups over roles.
        
        Returns:
            Dictionary with groups as keys and lists of names as values
        """
        # First, try to group by actual study groups (Group A, Group B, etc.)
        study_groups = defaultdict(list)
        role_groups = defaultdict(list)
        
        for participant in self.participants:
            group = participant.get("group", "Unknown")
            role = participant.get("role", "Unknown")
            name = participant.get("name", "")
            
            if not name:
                continue
            
            # Check if this is an actual study group (contains "Group" and a letter/number)
            if "group" in group.lower() and any(char.isalnum() for char in group if char not in "Group group"):
                study_groups[group].append(name)
            # If we have role information and it's more specific than the group
            elif role != "Unknown" and role != group:
                role_groups[role].append(name)
            # Otherwise use the group field
            else:
                if group == "Unknown" and role != "Unknown":
                    role_groups[role].append(name)
                else:
                    role_groups[group].append(name)
        
        # Combine and prioritize study groups
        final_groups = dict(study_groups)
        
        # Add role groups for those not in study groups
        for role, names in role_groups.items():
            if role not in final_groups:
                final_groups[role] = names
            else:
                # If there's overlap, add to existing group
                for name in names:
                    if name not in final_groups[role]:
                        final_groups[role].append(name)
        
        # Sort names within each group
        for group in final_groups:
            final_groups[group].sort()
        
        return final_groups
    
    def display_results(self):
        """Display the organized participant results."""
        if not self.participants:
            print("No participants found.")
            return
        
        groups = self.organize_by_groups()
        
        print("\n" + "="*60)
        print("MBAM601 PARTICIPANTS BY GROUP")
        print("="*60)
        
        total_participants = len(self.participants)
        print(f"Total Participants: {total_participants}\n")
        
        for group, names in sorted(groups.items()):
            print(f"{group} ({len(names)} members):")
            print("-" * 30)
            for name in names:
                print(f"  • {name}")
            print()
        
        # Create summary table
        print("SUMMARY:")
        print("-" * 30)
        for group, names in sorted(groups.items()):
            print(f"{group}: {len(names)} members")
    
    def generate_html_report(self) -> str:
        """
        Generate a modern HTML report of the participants with sorting functionality.
        
        Returns:
            HTML string containing the formatted report with university branding
        """
        if not self.participants:
            return "<html><body><h1>No participants found</h1></body></html>"
        
        groups = self.organize_by_groups()
        total_participants = len(self.participants)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get course name from target_course if available
        course_name = getattr(self, 'target_course', 'MBAM601')
        
        # Generate JSON data for JavaScript sorting
        participants_json = []
        for participant in self.participants:
            participants_json.append({
                'name': participant.get('name', 'Unknown'),
                'group': participant.get('group', 'No groups'),
                'role': participant.get('role', 'Unknown')
            })
        
        import json
        participants_data = json.dumps(participants_json)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course_name} Participants Report - University of Canterbury</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --uc-blue: #003366;
            --uc-light-blue: #0066cc;
            --uc-gold: #cc9900;
            --uc-green: #00aa44;
            --text-primary: #2d3436;
            --text-secondary: #636e72;
            --bg-light: #f8f9fa;
            --border-light: #e9ecef;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: linear-gradient(135deg, var(--uc-blue) 0%, var(--uc-light-blue) 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--uc-blue) 0%, var(--uc-light-blue) 100%);
            color: white;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            animation: float 20s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-20px) rotate(1deg); }}
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
            text-align: center;
        }}
        
        .uc-logo {{
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 12px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            font-size: 24px;
            color: var(--uc-blue);
            font-weight: 700;
        }}
        
        .header h1 {{
            font-size: 2.8rem;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
            margin-bottom: 30px;
        }}
        
        .header-actions {{
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.95rem;
        }}
        
        .btn-primary {{
            background: white;
            color: var(--uc-blue);
        }}
        
        .btn-primary:hover {{
            background: var(--bg-light);
            transform: translateY(-1px);
        }}
        
        .btn-secondary {{
            background: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .btn-secondary:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1px;
            background: var(--border-light);
            margin: 0;
        }}
        
        .stat-card {{
            background: white;
            padding: 32px 24px;
            text-align: center;
            transition: transform 0.2s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
        }}
        
        .stat-number {{
            font-size: 2.8rem;
            font-weight: 700;
            color: var(--uc-blue);
            margin-bottom: 8px;
            line-height: 1;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .controls {{
            background: var(--bg-light);
            padding: 24px 40px;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            gap: 16px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .controls label {{
            font-weight: 500;
            color: var(--text-primary);
            margin-right: 8px;
        }}
        
        .sort-select {{
            padding: 8px 12px;
            border: 1px solid var(--border-light);
            border-radius: 6px;
            background: white;
            font-family: inherit;
            font-size: 0.9rem;
            min-width: 150px;
        }}
        
        .search-box {{
            padding: 8px 12px;
            border: 1px solid var(--border-light);
            border-radius: 6px;
            background: white;
            font-family: inherit;
            font-size: 0.9rem;
            min-width: 200px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .participants-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }}
        
        .participants-table th {{
            background: linear-gradient(135deg, var(--uc-blue) 0%, var(--uc-light-blue) 100%);
            color: white;
            padding: 16px 20px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .participants-table td {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-light);
            transition: background-color 0.2s ease;
        }}
        
        .participants-table tr:hover td {{
            background-color: var(--bg-light);
        }}
        
        .participants-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .separator-row {{
            background: transparent !important;
        }}
        
        .separator-row:hover td {{
            background: transparent !important;
        }}
        
        .separator-cell {{
            padding: 24px 20px 16px 20px !important;
            border-bottom: none !important;
        }}
        
        .separator-content {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        
        .separator-text {{
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--uc-blue);
            white-space: nowrap;
            background: white;
            padding-right: 16px;
        }}
        
        .separator-line {{
            flex: 1;
            height: 2px;
            background: linear-gradient(90deg, var(--uc-blue) 0%, var(--border-light) 100%);
            border-radius: 1px;
        }}
        
        .participant-row td {{
            border-bottom: 1px solid var(--border-light);
        }}
        
        .participant-row:hover td {{
            background-color: var(--bg-light);
        }}
        
        .participant-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--uc-light-blue) 0%, var(--uc-green) 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            margin-right: 12px;
            font-size: 0.9rem;
        }}
        
        .participant-name {{
            font-weight: 500;
            color: var(--text-primary);
        }}
        
        .group-badge {{
            background: var(--uc-gold);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            white-space: nowrap;
        }}
        
        .role-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .role-student {{
            background: #e3f2fd;
            color: #1565c0;
        }}
        
        .role-lecturer {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .role-other {{
            background: #f1f8e9;
            color: #558b2f;
        }}
        
        .footer {{
            background: var(--bg-light);
            padding: 32px 40px;
            text-align: center;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-light);
        }}
        
        .footer p {{
            margin-bottom: 8px;
        }}
        
        .footer .timestamp {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 24px;
            }}
            
            .header h1 {{
                font-size: 2.2rem;
            }}
            
            .controls {{
                padding: 16px 24px;
                flex-direction: column;
                align-items: stretch;
            }}
            
            .content {{
                padding: 24px;
            }}
            
            .participants-table {{
                font-size: 0.9rem;
            }}
            
            .participants-table th,
            .participants-table td {{
                padding: 12px 16px;
            }}
        }}
        
        @media print {{
            body {{
                background: white !important;
                padding: 0 !important;
            }}
            
            .container {{
                box-shadow: none !important;
                border-radius: 0 !important;
            }}
            
            .btn, .controls {{
                display: none !important;
            }}
            
            .header {{
                background: var(--uc-blue) !important;
            }}
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }}
        
        .no-results i {{
            font-size: 3rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="uc-logo">UC</div>
                <h1>{course_name} Participants Report</h1>
                <div class="subtitle">University of Canterbury Business School</div>
                <div class="header-actions">
                    <button class="btn btn-primary" onclick="window.print()">
                        <i class="fas fa-print"></i> Print Report
                    </button>
                    <button class="btn btn-secondary" onclick="exportToCSV()">
                        <i class="fas fa-download"></i> Export CSV
                    </button>
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_participants}</div>
                <div class="stat-label">Total Participants</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(groups)}</div>
                <div class="stat-label">Study Groups</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([p for p in self.participants if 'student' in p.get('role', '').lower()])}</div>
                <div class="stat-label">Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len([p for p in self.participants if 'lecturer' in p.get('role', '').lower() or 'teacher' in p.get('role', '').lower()])}</div>
                <div class="stat-label">Staff</div>
            </div>
        </div>
        
        <div class="controls">
            <label for="sortSelect">Sort by:</label>
            <select id="sortSelect" class="sort-select" onchange="sortParticipants()">
                <option value="name">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
                <option value="group">Group</option>
                <option value="role">Role</option>
            </select>
            
            <label for="searchBox">Search:</label>
            <input type="text" id="searchBox" class="search-box" placeholder="Search participants..." onkeyup="filterParticipants()">
            
            <label for="groupFilter">Filter by Group:</label>
            <select id="groupFilter" class="sort-select" onchange="filterParticipants()">
                <option value="">All Groups</option>"""
        
        # Add group filter options
        for group_name in sorted(groups.keys()):
            if group_name != "No groups":
                html += f'<option value="{group_name}">{group_name}</option>'
        html += '<option value="No groups">No groups</option>'
        
        html += f"""
            </select>
        </div>
        
        <div class="content">
            <table class="participants-table" id="participantsTable">
                <thead>
                    <tr>
                        <th>Participant</th>
                        <th>Group</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody id="participantsBody">
                    <!-- Participants will be populated by JavaScript -->
                </tbody>
            </table>
            <div id="noResults" class="no-results" style="display: none;">
                <i class="fas fa-search"></i>
                <h3>No participants found</h3>
                <p>Try adjusting your search criteria or filters.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>University of Canterbury</strong> • Te Whare Wānanga o Waitaha</p>
            <p class="timestamp">Report generated on {current_time}</p>
        </div>
    </div>

    <script>
        // Participants data
        const participantsData = {participants_data};
        let filteredData = [...participantsData];

        function getInitials(name) {{
            return name.split(' ').map(word => word.charAt(0)).join('').substring(0, 2).toUpperCase();
        }}

        function getRoleClass(role) {{
            if (role.toLowerCase().includes('student')) return 'role-student';
            if (role.toLowerCase().includes('lecturer') || role.toLowerCase().includes('teacher')) return 'role-lecturer';
            return 'role-other';
        }}

        function renderParticipants(data) {{
            const tbody = document.getElementById('participantsBody');
            const noResults = document.getElementById('noResults');
            const sortBy = document.getElementById('sortSelect').value;
            
            if (data.length === 0) {{
                tbody.innerHTML = '';
                noResults.style.display = 'block';
                return;
            }}
            
            noResults.style.display = 'none';
            
            let html = '';
            let lastGroup = '';
            let lastRole = '';
            let lastName = '';
            
            data.forEach((participant, index) => {{
                let showSeparator = false;
                let separatorText = '';
                
                // Determine if we need a separator based on sort type
                if (sortBy === 'group' && participant.group !== lastGroup) {{
                    showSeparator = true;
                    separatorText = participant.group;
                    lastGroup = participant.group;
                }} else if (sortBy === 'role' && participant.role !== lastRole) {{
                    showSeparator = true;
                    separatorText = participant.role;
                    lastRole = participant.role;
                }} else if ((sortBy === 'name' || sortBy === 'name-desc') && participant.name.charAt(0).toUpperCase() !== lastName) {{
                    showSeparator = true;
                    separatorText = participant.name.charAt(0).toUpperCase();
                    lastName = participant.name.charAt(0).toUpperCase();
                }}
                
                // Add separator row if needed
                if (showSeparator && index > 0) {{
                    html += `
                        <tr class="separator-row">
                            <td colspan="3" class="separator-cell">
                                <div class="separator-content">
                                    <span class="separator-text">${{separatorText}}</span>
                                    <div class="separator-line"></div>
                                </div>
                            </td>
                        </tr>
                    `;
                }}
                
                // Add participant row
                html += `
                    <tr class="participant-row">
                        <td>
                            <div style="display: flex; align-items: center;">
                                <div class="participant-avatar">${{getInitials(participant.name)}}</div>
                                <span class="participant-name">${{participant.name}}</span>
                            </div>
                        </td>
                        <td>
                            <span class="group-badge">${{participant.group}}</span>
                        </td>
                        <td>
                            <span class="role-badge ${{getRoleClass(participant.role)}}">${{participant.role}}</span>
                        </td>
                    </tr>
                `;
            }});
            
            tbody.innerHTML = html;
        }}

        function sortParticipants() {{
            const sortBy = document.getElementById('sortSelect').value;
            
            filteredData.sort((a, b) => {{
                switch(sortBy) {{
                    case 'name':
                        return a.name.localeCompare(b.name);
                    case 'name-desc':
                        return b.name.localeCompare(a.name);
                    case 'group':
                        return a.group.localeCompare(b.group);
                    case 'role':
                        return a.role.localeCompare(b.role);
                    default:
                        return 0;
                }}
            }});
            
            renderParticipants(filteredData);
        }}

        function filterParticipants() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const groupFilter = document.getElementById('groupFilter').value;
            
            filteredData = participantsData.filter(participant => {{
                const matchesSearch = participant.name.toLowerCase().includes(searchTerm) ||
                                    participant.group.toLowerCase().includes(searchTerm) ||
                                    participant.role.toLowerCase().includes(searchTerm);
                                    
                const matchesGroup = !groupFilter || participant.group === groupFilter;
                
                return matchesSearch && matchesGroup;
            }});
            
            sortParticipants();
        }}

        function exportToCSV() {{
            const csvContent = [
                ['Name', 'Group', 'Role'],
                ...filteredData.map(p => [p.name, p.group, p.role])
            ].map(row => row.map(field => `"${{field}}"`).join(',')).join('\\n');
            
            const blob = new Blob([csvContent], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '{course_name.lower()}_participants.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }}

        // Initialize the table
        document.addEventListener('DOMContentLoaded', function() {{
            renderParticipants(participantsData);
        }});
    </script>
</body>
</html>
"""
        
        return html
    def save_results(self, filename: str = "mbam601_participants.json"):
        """
        Save results to a JSON file.
        
        Args:
            filename: Output filename
        """
        try:
            groups = self.organize_by_groups()
            
            data = {
                "course": "MBAM601",
                "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_participants": len(self.participants),
                "groups": groups,
                "raw_data": self.participants
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Results saved to {filename}")
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")
    
    def display_and_save_all_formats(self):
        """
        Display results in all available formats: console, JSON, and HTML browser.
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
        
        # 2. JSON save
        print("\n💾 JSON Export:")
        self.save_results()
        
        # 3. HTML browser display
        print("\n🌐 HTML Browser Display:")
        html_file = self.display_in_browser(save_file=True)
        
        print(f"\n✨ Results displayed in 3 formats:")
        print(f"   • Console output (above)")
        print(f"   • JSON file: mbam601_participants.json")
        if html_file:
            print(f"   • HTML report: {os.path.basename(html_file)}")
            print(f"   • Opened in your default browser")
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


def main():
    """Main function to run the scraper."""
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment or prompt user
    username = os.getenv('UC_USERNAME')
    password = os.getenv('UC_PASSWORD')
    
    if not username:
        username = input("Enter your UC Learn username: ")
    if not password:
        import getpass
        password = getpass.getpass("Enter your UC Learn password: ")
    
    # Initialize scraper - running in visible mode for debugging
    scraper = UCLearnScraper(headless=False)
    
    try:
        # Set up driver
        scraper.setup_driver()
        
        # Login
        if not scraper.login(username, password):
            print("Failed to login. Please check your credentials.")
            return
        
        # Find and navigate to MBAM601 course
        course_url = scraper.find_mbam601_course()
        if not course_url:
            print("Could not find or navigate to MBAM601 course. Please check if you're enrolled.")
            return
        
        # Navigate to participants (course_url may be current page now)
        if not scraper.navigate_to_participants(course_url):
            print("Could not access participants page. You might not have permission.")
            return
        
        # Extract participants
        participants = scraper.extract_participants()
        if not participants:
            print("No participants found. The page structure might have changed.")
            return
        
        # Display results in all formats
        scraper.display_and_save_all_formats()
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
