#!/home/coder/selenium-env/bin/python3
"""
E-commerce Website Testing with Selenium
Demonstrates real-world testing scenario for customer demo
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class EcommerceTest:
    """Test an e-commerce website (using a demo site)"""
    
    def __init__(self):
        """Initialize the test with Chrome options"""
        self.setup_driver()
        self.results = []
    
    def setup_driver(self):
        """Configure Chrome for headless testing"""
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
                break
        
        try:
            # Try Selenium Grid first
            self.driver = webdriver.Remote(
                command_executor='http://localhost:4444',
                options=chrome_options
            )
            print("✅ Connected to Selenium Grid")
        except:
            # Fallback to direct ChromeDriver
            from selenium.webdriver.chrome.service import Service
            service = Service('/home/coder/selenium-drivers/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Using direct ChromeDriver connection")
        
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)
    
    def log_result(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details
        }
        self.results.append(result)
        print(f"{result['status']} {test_name}: {details}")
    
    def test_homepage_load(self):
        """Test 1: Verify homepage loads correctly"""
        print("\n🏠 Testing Homepage Load...")
        
        try:
            # Using a real demo e-commerce site
            self.driver.get("https://www.saucedemo.com/")
            
            # Verify page loaded
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login_logo")))
            
            # Check title
            title = self.driver.title
            self.log_result("Homepage Load", True, f"Page title: {title}")
            
            # Take screenshot
            self.driver.save_screenshot("/home/coder/test_homepage.png")
            
            return True
            
        except Exception as e:
            self.log_result("Homepage Load", False, str(e))
            return False
    
    def test_user_login(self):
        """Test 2: Test user login functionality"""
        print("\n🔐 Testing User Login...")
        
        try:
            # Navigate to login page
            self.driver.get("https://www.saucedemo.com/")
            
            # Find login elements
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "user-name"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "login-button")
            
            # Enter credentials (using demo site credentials)
            username_field.send_keys("standard_user")
            password_field.send_keys("secret_sauce")
            
            # Click login
            login_button.click()
            
            # Verify login success
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
            )
            
            self.log_result("User Login", True, "Successfully logged in")
            self.driver.save_screenshot("/home/coder/test_login_success.png")
            
            return True
            
        except Exception as e:
            self.log_result("User Login", False, str(e))
            self.driver.save_screenshot("/home/coder/test_login_failed.png")
            return False
    
    def test_product_search_and_add_to_cart(self):
        """Test 3: Search for products and add to cart"""
        print("\n🛒 Testing Product Search and Add to Cart...")
        
        try:
            # Ensure we're logged in
            if "inventory" not in self.driver.current_url:
                self.test_user_login()
            
            # Find all products
            products = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "inventory_item"))
            )
            
            print(f"Found {len(products)} products")
            
            # Add first product to cart
            first_product = products[0]
            product_name = first_product.find_element(By.CLASS_NAME, "inventory_item_name").text
            add_button = first_product.find_element(By.CSS_SELECTOR, "button[class*='btn_inventory']")
            add_button.click()
            
            # Verify cart badge updated
            cart_badge = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
            )
            cart_count = cart_badge.text
            
            self.log_result(
                "Add to Cart", 
                True, 
                f"Added '{product_name}' to cart. Cart count: {cart_count}"
            )
            
            # Add another product
            products[1].find_element(By.CSS_SELECTOR, "button[class*='btn_inventory']").click()
            time.sleep(1)
            
            # Check updated cart count
            cart_count = self.driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
            self.log_result("Multiple Items", True, f"Cart now has {cart_count} items")
            
            return True
            
        except Exception as e:
            self.log_result("Add to Cart", False, str(e))
            return False
    
    def test_checkout_process(self):
        """Test 4: Test the checkout process"""
        print("\n💳 Testing Checkout Process...")
        
        try:
            # Click on cart
            cart_link = self.driver.find_element(By.CLASS_NAME, "shopping_cart_link")
            cart_link.click()
            
            # Verify we're in the cart
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cart_list")))
            
            # Get cart items
            cart_items = self.driver.find_elements(By.CLASS_NAME, "cart_item")
            self.log_result("Cart Page", True, f"Cart contains {len(cart_items)} items")
            
            # Proceed to checkout
            checkout_button = self.driver.find_element(By.ID, "checkout")
            checkout_button.click()
            
            # Fill checkout information
            self.wait.until(EC.presence_of_element_located((By.ID, "first-name")))
            
            self.driver.find_element(By.ID, "first-name").send_keys("Test")
            self.driver.find_element(By.ID, "last-name").send_keys("User")
            self.driver.find_element(By.ID, "postal-code").send_keys("12345")
            
            # Continue
            continue_button = self.driver.find_element(By.ID, "continue")
            continue_button.click()
            
            # Verify checkout overview page
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "summary_info")))
            
            # Get total price
            total_label = self.driver.find_element(By.CLASS_NAME, "summary_total_label")
            total_price = total_label.text
            
            self.log_result("Checkout Process", True, f"Order total: {total_price}")
            self.driver.save_screenshot("/home/coder/test_checkout_overview.png")
            
            # Complete order
            finish_button = self.driver.find_element(By.ID, "finish")
            finish_button.click()
            
            # Verify order completion
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "complete-header")))
            complete_text = self.driver.find_element(By.CLASS_NAME, "complete-header").text
            
            self.log_result("Order Completion", True, complete_text)
            self.driver.save_screenshot("/home/coder/test_order_complete.png")
            
            return True
            
        except Exception as e:
            self.log_result("Checkout Process", False, str(e))
            return False
    
    def test_responsive_design(self):
        """Test 5: Test responsive design on different screen sizes"""
        print("\n📱 Testing Responsive Design...")
        
        try:
            # Navigate to homepage
            self.driver.get("https://www.saucedemo.com/")
            
            # Test different screen sizes
            screen_sizes = [
                {"name": "Mobile", "width": 375, "height": 667},
                {"name": "Tablet", "width": 768, "height": 1024},
                {"name": "Desktop", "width": 1920, "height": 1080}
            ]
            
            for size in screen_sizes:
                self.driver.set_window_size(size["width"], size["height"])
                time.sleep(1)  # Allow time for responsive adjustments
                
                # Take screenshot
                filename = f"/home/coder/test_responsive_{size['name'].lower()}.png"
                self.driver.save_screenshot(filename)
                
                # Verify key elements are visible
                login_logo = self.driver.find_element(By.CLASS_NAME, "login_logo")
                is_displayed = login_logo.is_displayed()
                
                self.log_result(
                    f"Responsive - {size['name']}", 
                    is_displayed, 
                    f"{size['width']}x{size['height']} - Logo visible: {is_displayed}"
                )
            
            return True
            
        except Exception as e:
            self.log_result("Responsive Design", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all e-commerce tests"""
        print("\n" + "="*60)
        print("🛍️  E-COMMERCE WEBSITE TESTING SUITE")
        print("="*60)
        
        # Run tests
        self.test_homepage_load()
        self.test_user_login()
        self.test_product_search_and_add_to_cart()
        self.test_checkout_process()
        self.test_responsive_design()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if "PASS" in r["status"])
        failed = sum(1 for r in self.results if "FAIL" in r["status"])
        
        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        
        print("\nDetailed Results:")
        for result in self.results:
            print(f"  {result['status']} {result['test']}")
            if result['details']:
                print(f"     → {result['details']}")
        
        # Generate HTML report
        self.generate_html_report()
    
    def generate_html_report(self):
        """Generate an HTML report of test results"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Selenium Test Report - Coder Workspace</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .screenshot {{ margin: 10px 0; }}
                img {{ max-width: 400px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>🛍️ E-commerce Testing Report</h1>
            <p>Generated from Coder Workspace Selenium Tests</p>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <p>Total Tests: {len(self.results)}</p>
                <p class="pass">✅ Passed: {sum(1 for r in self.results if "PASS" in r["status"])}</p>
                <p class="fail">❌ Failed: {sum(1 for r in self.results if "FAIL" in r["status"])}</p>
            </div>
            
            <h2>Test Results</h2>
            <table>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
        """
        
        for result in self.results:
            status_class = "pass" if "PASS" in result["status"] else "fail"
            html_content += f"""
                <tr>
                    <td>{result['test']}</td>
                    <td class="{status_class}">{result['status']}</td>
                    <td>{result['details']}</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h2>Screenshots</h2>
            <p>Screenshots are saved in /home/coder/ directory</p>
            
            <div class="screenshot">
                <h3>Homepage</h3>
                <img src="test_homepage.png" alt="Homepage Screenshot">
            </div>
            
            <div class="screenshot">
                <h3>Checkout Overview</h3>
                <img src="test_checkout_overview.png" alt="Checkout Screenshot">
            </div>
            
            <div class="screenshot">
                <h3>Order Complete</h3>
                <img src="test_order_complete.png" alt="Order Complete Screenshot">
            </div>
        </body>
        </html>
        """
        
        # Save report
        with open("/home/coder/test_report.html", "w") as f:
            f.write(html_content)
        
        print("\n📄 HTML report generated: /home/coder/test_report.html")
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()


if __name__ == "__main__":
    # Create and run test suite
    tester = EcommerceTest()
    
    try:
        tester.run_all_tests()
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
    finally:
        tester.cleanup()
        print("\n✅ Test execution completed!")
