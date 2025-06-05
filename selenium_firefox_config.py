#!/usr/bin/env python3
"""
Firefox configuration module for Selenium tests
Use this as an alternative if Chrome has issues
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
import tempfile
import os


def get_firefox_driver(grid_url):
    """
    Create a Firefox WebDriver instance with proper configuration
    """
    firefox_options = FirefoxOptions()
    
    # Run in headless mode
    firefox_options.add_argument('--headless')
    
    # Set window size
    firefox_options.add_argument('--width=1920')
    firefox_options.add_argument('--height=1080')
    
    # Create unique profile directory
    temp_dir = tempfile.mkdtemp(prefix='firefox_test_')
    firefox_options.add_argument(f'-profile')
    firefox_options.add_argument(temp_dir)
    
    # Additional Firefox preferences
    firefox_options.set_preference('browser.download.folderList', 2)
    firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
    firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')
    firefox_options.set_preference('browser.cache.disk.enable', False)
    firefox_options.set_preference('browser.cache.memory.enable', False)
    firefox_options.set_preference('browser.cache.offline.enable', False)
    firefox_options.set_preference('network.http.use-cache', False)
    
    # Security preferences
    firefox_options.set_preference('security.fileuri.strict_origin_policy', False)
    firefox_options.set_preference('permissions.default.image', 2)  # Disable images for faster loading
    
    try:
        driver = webdriver.Remote(
            command_executor=grid_url,
            options=firefox_options
        )
        return driver, temp_dir
    except Exception as e:
        # Clean up temp directory if driver creation fails
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise e


def get_chrome_driver_alternative(grid_url):
    """
    Alternative Chrome configuration with different settings
    """
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    
    chrome_options = ChromeOptions()
    
    # Basic options
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Create unique temp directory with timestamp
    import time
    timestamp = str(int(time.time() * 1000))
    temp_dir = f"/tmp/chrome_test_{timestamp}_{os.getpid()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    chrome_options.add_argument(f'--user-data-dir={temp_dir}')
    
    # Additional stability options
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Memory optimization
    chrome_options.add_argument('--memory-pressure-off')
    chrome_options.add_argument('--max_old_space_size=4096')
    
    # Disable features that might cause conflicts
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    
    # Set explicit binary location if needed
    # chrome_options.binary_location = '/usr/bin/chromium-browser'
    
    try:
        driver = webdriver.Remote(
            command_executor=grid_url,
            options=chrome_options
        )
        return driver, temp_dir
    except Exception as e:
        # Clean up temp directory if driver creation fails
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise e


# Modified setUp method that can switch between browsers
def flexible_setUp(self, browser='chrome'):
    """
    Flexible setUp that can use different browsers
    """
    self.test_start = time.time()
    self.logger.info(f"Starting test: {self._testMethodName} with {browser}")
    
    try:
        if browser.lower() == 'firefox':
            self.driver, self.temp_dir = get_firefox_driver(self.grid_url)
        else:
            self.driver, self.temp_dir = get_chrome_driver_alternative(self.grid_url)
        
        self.driver.set_window_size(1920, 1080)
        self.browser_type = browser
        
    except Exception as e:
        self.logger.error(f"Failed to connect to Selenium Grid with {browser}: {e}")
        # Try alternative browser
        if browser.lower() == 'chrome':
            self.logger.info("Trying Firefox as fallback...")
            try:
                self.driver, self.temp_dir = get_firefox_driver(self.grid_url)
                self.driver.set_window_size(1920, 1080)
                self.browser_type = 'firefox'
                self.logger.info("Successfully switched to Firefox")
            except Exception as e2:
                self.logger.error(f"Firefox also failed: {e2}")
                raise
        else:
            raise


# Standalone test script to verify Selenium Grid connection
if __name__ == "__main__":
    import logging
    import sys
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    grid_url = "http://localhost:4444/wd/hub"
    
    # Test Chrome
    logger.info("Testing Chrome connection...")
    try:
        driver, temp_dir = get_chrome_driver_alternative(grid_url)
        driver.get("http://localhost:4444/ui")
        logger.info(f"Chrome connected successfully. Title: {driver.title}")
        driver.quit()
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Chrome failed: {e}")
    
    # Test Firefox
    logger.info("\nTesting Firefox connection...")
    try:
        driver, temp_dir = get_firefox_driver(grid_url)
        driver.get("http://localhost:4444/ui")
        logger.info(f"Firefox connected successfully. Title: {driver.title}")
        driver.quit()
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Firefox failed: {e}")
