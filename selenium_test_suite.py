#!/usr/bin/env python3
"""
Selenium Grid Test Suite for Coder Workspace
This script demonstrates automated testing using Selenium Grid with comprehensive logging
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import unittest
import argparse
from typing import Dict, List, Any

# Configure logging
def setup_logging(log_dir: str = "test_logs") -> logging.Logger:
    """Setup comprehensive logging for test execution"""
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"selenium_tests_{timestamp}.log")
    
    # Create logger
    logger = logging.getLogger('SeleniumTests')
    logger.setLevel(logging.DEBUG)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for summary
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler.setFormatter(detailed_formatter)
    console_handler.setFormatter(simple_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Test Results Logger
class TestResultsLogger:
    """Handles test results logging in multiple formats"""
    
    def __init__(self, log_dir: str = "test_logs"):
        self.log_dir = log_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "test_run": {
                "timestamp": self.timestamp,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            },
            "test_cases": []
        }
    
    def log_test_case(self, test_case: Dict[str, Any]):
        """Log individual test case result"""
        self.results["test_cases"].append(test_case)
        
        # Update counters
        if test_case["status"] == "PASS":
            self.results["test_run"]["passed"] += 1
        elif test_case["status"] == "FAIL":
            self.results["test_run"]["failed"] += 1
        elif test_case["status"] == "ERROR":
            self.results["test_run"]["errors"] += 1
        elif test_case["status"] == "SKIP":
            self.results["test_run"]["skipped"] += 1
        
        self.results["test_run"]["total_tests"] += 1
    
    def finalize(self):
        """Finalize and save test results"""
        self.results["test_run"]["end_time"] = datetime.now().isoformat()
        
        # Save JSON report
        json_file = os.path.join(self.log_dir, f"test_results_{self.timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save HTML report
        html_file = os.path.join(self.log_dir, f"test_report_{self.timestamp}.html")
        self._generate_html_report(html_file)
        
        return json_file, html_file
    
    def _generate_html_report(self, filename: str):
        """Generate HTML test report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Selenium Test Report - {self.timestamp}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                .error {{ color: orange; }}
                .skip {{ color: gray; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .screenshot {{ max-width: 100px; cursor: pointer; }}
                .modal {{ display: none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
                .modal-content {{ margin: 15% auto; display: block; width: 80%; max-width: 700px; }}
            </style>
        </head>
        <body>
            <h1>Selenium Test Report</h1>
            <div class="summary">
                <h2>Test Summary</h2>
                <p><strong>Test Run:</strong> {self.results['test_run']['timestamp']}</p>
                <p><strong>Duration:</strong> {self.results['test_run']['start_time']} to {self.results['test_run']['end_time']}</p>
                <p><strong>Total Tests:</strong> {self.results['test_run']['total_tests']}</p>
                <p class="pass"><strong>Passed:</strong> {self.results['test_run']['passed']}</p>
                <p class="fail"><strong>Failed:</strong> {self.results['test_run']['failed']}</p>
                <p class="error"><strong>Errors:</strong> {self.results['test_run']['errors']}</p>
                <p class="skip"><strong>Skipped:</strong> {self.results['test_run']['skipped']}</p>
            </div>
            
            <h2>Test Details</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration (s)</th>
                    <th>Error Message</th>
                    <th>Screenshot</th>
                </tr>
        """
        
        for test in self.results['test_cases']:
            status_class = test['status'].lower()
            error_msg = test.get('error_message', '-')
            screenshot = test.get('screenshot', '-')
            
            html_content += f"""
                <tr>
                    <td>{test['name']}</td>
                    <td class="{status_class}">{test['status']}</td>
                    <td>{test['duration']:.2f}</td>
                    <td>{error_msg}</td>
                    <td>{'<img class="screenshot" src="' + screenshot + '" onclick="openModal(this.src)">' if screenshot != '-' else '-'}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <div id="modal" class="modal" onclick="closeModal()">
                <img class="modal-content" id="modalImg">
            </div>
            
            <script>
                function openModal(src) {
                    document.getElementById('modal').style.display = "block";
                    document.getElementById('modalImg').src = src;
                }
                
                function closeModal() {
                    document.getElementById('modal').style.display = "none";
                }
            </script>
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_content)

# Base Test Class
class SeleniumGridTest(unittest.TestCase):
    """Base class for Selenium Grid tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger('SeleniumTests')
        cls.results_logger = TestResultsLogger()
        cls.grid_url = "http://localhost:4444/wd/hub"
        cls.screenshots_dir = "test_logs/screenshots"
        os.makedirs(cls.screenshots_dir, exist_ok=True)
    
    def setUp(self):
        """Set up test driver"""
        self.test_start = time.time()
        self.logger.info(f"Starting test: {self._testMethodName}")
        
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--headless')  # Run in headless mode
        
        try:
            self.driver = webdriver.Remote(
                command_executor=self.grid_url,
                options=chrome_options
            )
            self.driver.set_window_size(1920, 1080)
        except Exception as e:
            self.logger.error(f"Failed to connect to Selenium Grid: {e}")
            raise
    
    def tearDown(self):
        """Clean up after test"""
        test_duration = time.time() - self.test_start
        test_name = self._testMethodName
        
        # Determine test status
        if hasattr(self, '_outcome'):
            result = self._outcome.result
            if result.failures:
                status = "FAIL"
                error_msg = str(result.failures[-1][1])
            elif result.errors:
                status = "ERROR"
                error_msg = str(result.errors[-1][1])
            else:
                status = "PASS"
                error_msg = None
        else:
            status = "UNKNOWN"
            error_msg = None
        
        # Take screenshot for failed tests
        screenshot_path = None
        if status in ["FAIL", "ERROR"] and hasattr(self, 'driver'):
            screenshot_name = f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = os.path.join(self.screenshots_dir, screenshot_name)
            try:
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                self.logger.error(f"Failed to save screenshot: {e}")
        
        # Log test result
        test_result = {
            "name": test_name,
            "status": status,
            "duration": test_duration,
            "error_message": error_msg,
            "screenshot": screenshot_path
        }
        self.results_logger.log_test_case(test_result)
        
        # Close driver
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        self.logger.info(f"Test {test_name} completed: {status} ({test_duration:.2f}s)")

# Sample Test Cases
class WebApplicationTests(SeleniumGridTest):
    """Sample web application tests"""
    
    def test_google_search(self):
        """Test Google search functionality"""
        self.driver.get("https://www.google.com")
        
        # Accept cookies if present
        try:
            accept_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept')]"))
            )
            accept_button.click()
        except TimeoutException:
            pass
        
        # Perform search
        search_box = self.driver.find_element(By.NAME, "q")
        search_box.send_keys("Coder.com")
        search_box.submit()
        
        # Wait for results
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        # Verify results
        results = self.driver.find_elements(By.CSS_SELECTOR, "h3")
        self.assertGreater(len(results), 0, "No search results found")
        self.logger.info(f"Found {len(results)} search results")
    
    def test_coder_website(self):
        """Test Coder.com website loading"""
        self.driver.get("https://coder.com")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verify title
        self.assertIn("Coder", self.driver.title)
        
        # Check for main elements
        try:
            header = self.driver.find_element(By.TAG_NAME, "header")
            self.assertIsNotNone(header, "Header not found")
            self.logger.info("Coder website loaded successfully")
        except NoSuchElementException:
            self.fail("Failed to find header element")
    
    def test_github_coder_repo(self):
        """Test GitHub Coder repository page"""
        self.driver.get("https://github.com/coder/coder")
        
        # Wait for repository content
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-pjax='#repo-content-pjax-container']"))
        )
        
        # Verify repository name
        repo_name = self.driver.find_element(By.CSS_SELECTOR, "strong[itemprop='name'] a")
        self.assertEqual(repo_name.text.lower(), "coder")
        
        # Check for README
        readme = self.driver.find_element(By.CSS_SELECTOR, "article")
        self.assertIsNotNone(readme, "README not found")
        self.logger.info("GitHub repository page verified")
    
    def test_selenium_grid_console(self):
        """Test Selenium Grid console accessibility"""
        self.driver.get("http://localhost:4444/ui")
        
        # Wait for Grid console to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verify we're on the Grid console
        self.assertIn("Selenium Grid", self.driver.title)
        self.logger.info("Selenium Grid console is accessible")

# Test Runner
def run_tests(test_suite: str = "all"):
    """Run the test suite"""
    logger = setup_logging()
    logger.info(f"Starting Selenium Grid test suite: {test_suite}")
    
    # Create test suite
    if test_suite == "all":
        suite = unittest.TestLoader().loadTestsFromTestCase(WebApplicationTests)
    else:
        suite = unittest.TestSuite()
        suite.addTest(WebApplicationTests(test_suite))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Finalize results
    results_logger = WebApplicationTests.results_logger
    json_report, html_report = results_logger.finalize()
    
    logger.info(f"Test execution completed")
    logger.info(f"JSON report: {json_report}")
    logger.info(f"HTML report: {html_report}")
    
    # Return exit code based on results
    return 0 if result.wasSuccessful() else 1

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Selenium Grid tests")
    parser.add_argument(
        "--test",
        default="all",
        help="Specific test to run (default: all)"
    )
    parser.add_argument(
        "--grid-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid URL"
    )
    
    args = parser.parse_args()
    
    # Update grid URL if provided
    if args.grid_url:
        SeleniumGridTest.grid_url = args.grid_url
    
    # Run tests
    exit_code = run_tests(args.test)
    sys.exit(exit_code)