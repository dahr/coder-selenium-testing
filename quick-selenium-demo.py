#!/home/coder/selenium-env/bin/python3
"""
Quick Selenium Demo - Ready to run in Coder Workspace
Shows that Selenium automation is working correctly
"""

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def main():
    print_banner("🚀 SELENIUM AUTOMATION DEMO - CODER WORKSPACE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configure Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Find Chrome binary
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium'
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_options.binary_location = path
            print(f"✅ Found Chrome at: {path}")
            break
    
    # Initialize driver
    driver = None
    try:
        # Try Selenium Grid first
        print("\n🔌 Attempting to connect to Selenium Grid...")
        driver = webdriver.Remote(
            command_executor='http://localhost:4444',
            options=chrome_options
        )
        print("✅ Connected to Selenium Grid successfully!")
        
    except Exception as e:
        print(f"⚠️  Grid connection failed: {e}")
        print("🔄 Falling back to direct ChromeDriver...")
        
        from selenium.webdriver.chrome.service import Service
        service = Service('/home/coder/selenium-drivers/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Connected via direct ChromeDriver!")
    
    # Run demo tests
    print_banner("🧪 RUNNING AUTOMATED TESTS")
    
    try:
        # Test 1: Google Search
        print("\n📍 Test 1: Automated Google Search")
        driver.get("https://www.google.com")
        print(f"   → Navigated to: {driver.title}")
        
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Coder development environments")
        search_box.submit()
        
        time.sleep(2)  # Wait for results
        print("   → Search completed successfully")
        
        # Take screenshot
        screenshot_path = "/home/coder/demo_google_search.png"
        driver.save_screenshot(screenshot_path)
        print(f"   → Screenshot saved: {screenshot_path}")
        
        # Test 2: Navigate multiple sites
        print("\n📍 Test 2: Multi-Site Navigation")
        sites = [
            ("https://github.com", "GitHub"),
            ("https://coder.com", "Coder"),
            ("https://example.com", "Example Domain")
        ]
        
        for url, expected in sites:
            driver.get(url)
            time.sleep(1)
            print(f"   → Visited {url} - Title: {driver.title}")
        
        # Test 3: JavaScript execution
        print("\n📍 Test 3: JavaScript Automation")
        driver.get("https://example.com")
        
        # Inject custom content
        driver.execute_script("""
            document.body.innerHTML += '<div id="coder-test" style="background: #4CAF50; color: white; padding: 20px; margin: 20px; text-align: center; font-size: 24px;">Automated by Selenium in Coder Workspace!</div>';
        """)
        
        # Take screenshot of modified page
        screenshot_path = "/home/coder/demo_js_injection.png"
        driver.save_screenshot(screenshot_path)
        print(f"   → Modified page with JavaScript")
        print(f"   → Screenshot saved: {screenshot_path}")
        
        # Test 4: Performance metrics
        print("\n📍 Test 4: Performance Metrics")
        driver.get("https://www.google.com")
        
        # Get performance timing
        performance_timing = driver.execute_script("""
            return {
                loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                resources: performance.getEntriesByType('resource').length
            }
        """)
        
        print(f"   → Page Load Time: {performance_timing['loadTime']}ms")
        print(f"   → DOM Ready Time: {performance_timing['domReady']}ms")
        print(f"   → Resources Loaded: {performance_timing['resources']}")
        
        print_banner("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        
        # Summary
        print("\n📊 DEMO SUMMARY:")
        print("   • Selenium Grid/ChromeDriver: ✅ Working")
        print("   • Chrome Browser: ✅ Installed and functional")
        print("   • Web Navigation: ✅ Successful")
        print("   • JavaScript Execution: ✅ Working")
        print("   • Screenshot Capture: ✅ Working")
        print("   • Performance Metrics: ✅ Captured")
        
        print("\n📁 Generated Files:")
        print("   • /home/coder/demo_google_search.png")
        print("   • /home/coder/demo_js_injection.png")
        
        print("\n🎯 Next Steps:")
        print("   1. Run the comprehensive test suite: ./selenium-test-suite.py")
        print("   2. Run e-commerce tests: ./ecommerce-selenium-test.py")
        print("   3. Check Selenium status: ./check-selenium.sh")
        print("   4. View test artifacts in the file browser")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("\n🧹 Cleanup completed - browser closed")
    
    print(f"\n⏱️  Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
