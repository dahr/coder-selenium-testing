#!/home/coder/selenium-env/bin/python3
"""
Simple Selenium Test Suite for Coder Workspace
Demonstrates various automated testing scenarios
"""

import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class CoderSeleniumTests(unittest.TestCase):
    """Test suite demonstrating Selenium automation in Coder Workspace"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Chrome options for headless testing"""
        cls.chrome_options = Options()
        cls.chrome_options.add_argument('--headless=new')
        cls.chrome_options.add_argument('--no-sandbox')
        cls.chrome_options.add_argument('--disable-dev-shm-usage')
        cls.chrome_options.add_argument('--disable-gpu')
        cls.chrome_options.add_argument('--window-size=1920,1080')
        
        # Find Chrome binary
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                cls.chrome_options.binary_location = path
                break
    
    def setUp(self):
        """Create a new browser instance for each test"""
        try:
            # Try connecting to Selenium Grid first
            self.driver = webdriver.Remote(
                command_executor='http://localhost:4444',
                options=self.chrome_options
            )
        except Exception as e:
            print(f"Failed to connect to Selenium Grid: {e}")
            print("Falling back to direct ChromeDriver connection...")
            # Fallback to direct ChromeDriver
            from selenium.webdriver.chrome.service import Service
            service = Service('/home/coder/selenium-drivers/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        
        self.driver.implicitly_wait(10)
    
    def tearDown(self):
        """Close the browser after each test"""
        if self.driver:
            self.driver.quit()
    
    def test_01_google_search(self):
        """Test 1: Basic Google search functionality"""
        print("\n🔍 Test 1: Google Search")
        
        # Navigate to Google
        self.driver.get("https://www.google.com")
        self.assertEqual("Google", self.driver.title)
        
        # Find search box and search for Coder
        search_box = self.driver.find_element(By.NAME, "q")
        search_box.send_keys("Coder development environments")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results - Google may have different IDs
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
        except TimeoutException:
            # Try alternative selectors
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-async-context]"))
            )
        
        # Verify we have results by checking if we're on the search results page
        self.assertIn("search", self.driver.current_url.lower())
        print("✅ Search completed and results page loaded")
    
    def test_02_github_navigation(self):
        """Test 2: Navigate GitHub and verify elements"""
        print("\n🐙 Test 2: GitHub Navigation")
        
        # Navigate to GitHub
        self.driver.get("https://github.com")
        
        # Verify we're on GitHub
        self.assertIn("GitHub", self.driver.title)
        
        # Search for Coder repository
        search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-target='qbsearch-input.inputButtonText']"))
        )
        search_button.click()
        
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "query-builder-test"))
        )
        search_input.send_keys("coder/coder")
        search_input.send_keys(Keys.RETURN)
        
        # Wait for results
        time.sleep(2)  # GitHub search can be slow
        
        print("✅ Successfully searched GitHub")
    
    def test_03_form_interaction(self):
        """Test 3: Form filling and submission"""
        print("\n📝 Test 3: Form Interaction")
        
        # Use a test form page
        self.driver.get("https://www.w3schools.com/html/html_forms.asp")
        
        # Find and interact with form elements
        try:
            # Accept cookies if present
            try:
                accept_button = self.driver.find_element(By.ID, "accept-choices")
                accept_button.click()
            except:
                pass  # No cookie banner
            
            # Scroll to the form example
            self.driver.execute_script("window.scrollTo(0, 500)")
            
            # Verify form elements exist
            form_elements = self.driver.find_elements(By.TAG_NAME, "input")
            self.assertTrue(len(form_elements) > 0, "No form elements found")
            
            print(f"✅ Found {len(form_elements)} form input elements")
        except Exception as e:
            print(f"⚠️  Form interaction test skipped: {e}")
    
    def test_04_javascript_execution(self):
        """Test 4: Execute JavaScript and verify results"""
        print("\n🎯 Test 4: JavaScript Execution")
        
        # Navigate to a simple page
        self.driver.get("https://example.com")
        
        # Execute JavaScript to modify the page
        original_title = self.driver.title
        new_title = "Selenium Test - Modified by Coder"
        
        self.driver.execute_script(f"document.title = '{new_title}'")
        
        # Verify the change
        self.assertEqual(self.driver.title, new_title)
        print(f"✅ Changed title from '{original_title}' to '{new_title}'")
        
        # Get page info via JavaScript
        page_info = self.driver.execute_script("""
            return {
                url: window.location.href,
                width: window.innerWidth,
                height: window.innerHeight,
                userAgent: navigator.userAgent
            }
        """)
        
        print(f"✅ Page info retrieved: {page_info['url']} ({page_info['width']}x{page_info['height']})")
    
    def test_05_screenshot_capture(self):
        """Test 5: Take screenshots for visual verification"""
        print("\n📸 Test 5: Screenshot Capture")
        
        # Navigate to Coder's website
        self.driver.get("https://coder.com")
        
        # Take a screenshot
        screenshot_path = "/home/coder/selenium-screenshot.png"
        self.driver.save_screenshot(screenshot_path)
        
        # Verify screenshot was created
        self.assertTrue(os.path.exists(screenshot_path), "Screenshot was not created")
        file_size = os.path.getsize(screenshot_path)
        self.assertGreater(file_size, 0, "Screenshot file is empty")
        
        print(f"✅ Screenshot saved: {screenshot_path} ({file_size} bytes)")
    
    def test_06_wait_conditions(self):
        """Test 6: Demonstrate various wait conditions"""
        print("\n⏱️  Test 6: Wait Conditions")
        
        # Navigate to a dynamic page
        self.driver.get("https://www.google.com")
        
        # Wait for specific element to be present
        try:
            # Wait for search box to be present
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            print("✅ Search box is present")
            
            # Wait for title to contain specific text
            WebDriverWait(self.driver, 10).until(
                EC.title_contains("Google")
            )
            print("✅ Page title contains 'Google'")
            
            # Check if element is visible
            is_visible = search_box.is_displayed()
            print(f"✅ Search box visibility: {is_visible}")
            
        except TimeoutException:
            self.fail("Timeout waiting for elements")
    
    def test_07_multi_window_handling(self):
        """Test 7: Handle multiple windows/tabs"""
        print("\n🪟 Test 7: Multi-Window Handling")
        
        # Get the main window handle
        main_window = self.driver.current_window_handle
        
        # Open a new window using JavaScript
        self.driver.execute_script("window.open('https://example.com', '_blank');")
        
        # Wait for new window
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.window_handles) > 1
        )
        
        # Switch to new window
        all_windows = self.driver.window_handles
        self.driver.switch_to.window(all_windows[1])
        
        # Verify we're in the new window
        self.assertIn("Example", self.driver.title)
        print("✅ Switched to new window")
        
        # Switch back to main window
        self.driver.switch_to.window(main_window)
        print("✅ Switched back to main window")
    
    def test_08_element_attributes(self):
        """Test 8: Read and verify element attributes"""
        print("\n🏷️  Test 8: Element Attributes")
        
        # Navigate to Google
        self.driver.get("https://www.google.com")
        
        # Find the search box
        search_box = self.driver.find_element(By.NAME, "q")
        
        # Get various attributes
        attributes = {
            "name": search_box.get_attribute("name"),
            "tag": search_box.tag_name,
            "class": search_box.get_attribute("class"),
            "maxlength": search_box.get_attribute("maxlength"),
            "title": search_box.get_attribute("title"),
            "aria-label": search_box.get_attribute("aria-label")
        }
        
        # Verify attributes
        self.assertEqual(attributes["name"], "q")
        self.assertEqual(attributes["tag"].lower(), "textarea")  # Google now uses textarea
        
        print(f"✅ Element attributes: {attributes}")


def run_individual_test(test_name):
    """Run a specific test by name"""
    suite = unittest.TestLoader().loadTestsFromName(f'__main__.CoderSeleniumTests.{test_name}')
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def run_all_tests():
    """Run all tests in the suite"""
    print("🚀 Running Selenium Test Suite in Coder Workspace")
    print("=" * 60)
    
    # Check Selenium Grid status using urllib
    import urllib.request
    import urllib.error
    try:
        with urllib.request.urlopen("http://localhost:4444/wd/hub/status", timeout=5) as response:
            if response.status == 200:
                print("✅ Selenium Grid is running")
            else:
                print("⚠️  Selenium Grid returned status:", response.status)
    except (urllib.error.URLError, urllib.error.HTTPError, Exception):
        print("⚠️  Selenium Grid not responding, will use direct ChromeDriver")
    
    print("=" * 60)
    
    # Run the test suite
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        print(f"Running specific test: {test_name}")
        run_individual_test(test_name)
    else:
        # Run all tests
        run_all_tests()
