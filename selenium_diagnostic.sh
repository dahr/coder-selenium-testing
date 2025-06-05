#!/bin/bash

# Selenium Grid Diagnostic Script
# This script helps diagnose and fix common Selenium Grid issues

echo "======================================"
echo "Selenium Grid Diagnostic Tool"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check functions
check_java() {
    echo -n "Checking Java installation... "
    if command -v java &> /dev/null; then
        java_version=$(java -version 2>&1 | head -n 1)
        echo -e "${GREEN}OK${NC} - $java_version"
        return 0
    else
        echo -e "${RED}NOT FOUND${NC}"
        return 1
    fi
}

check_browsers() {
    echo "Checking browser installations:"
    
    # Chrome/Chromium
    echo -n "  Chrome/Chromium... "
    if command -v google-chrome &> /dev/null; then
        version=$(google-chrome --version 2>/dev/null)
        echo -e "${GREEN}OK${NC} - $version"
    elif command -v chromium-browser &> /dev/null; then
        version=$(chromium-browser --version 2>/dev/null)
        echo -e "${GREEN}OK${NC} - $version"
    else
        echo -e "${RED}NOT FOUND${NC}"
    fi
    
    # Firefox
    echo -n "  Firefox... "
    if command -v firefox &> /dev/null; then
        version=$(firefox --version 2>/dev/null)
        echo -e "${GREEN}OK${NC} - $version"
    else
        echo -e "${RED}NOT FOUND${NC}"
    fi
}

check_drivers() {
    echo "Checking WebDriver installations:"
    
    # ChromeDriver
    echo -n "  ChromeDriver... "
    if command -v chromedriver &> /dev/null; then
        version=$(chromedriver --version 2>/dev/null | head -n 1)
        echo -e "${GREEN}OK${NC} - $version"
    else
        echo -e "${RED}NOT FOUND${NC}"
    fi
    
    # GeckoDriver
    echo -n "  GeckoDriver... "
    if command -v geckodriver &> /dev/null; then
        version=$(geckodriver --version 2>/dev/null | head -n 1)
        echo -e "${GREEN}OK${NC} - $version"
    else
        echo -e "${RED}NOT FOUND${NC}"
    fi
}

check_processes() {
    echo "Checking for running browser processes:"
    
    chrome_procs=$(pgrep -f "chrome|chromium" | wc -l)
    firefox_procs=$(pgrep -f "firefox" | wc -l)
    
    if [ $chrome_procs -gt 0 ]; then
        echo -e "  ${YELLOW}Chrome/Chromium processes:${NC} $chrome_procs running"
        echo "    PIDs: $(pgrep -f 'chrome|chromium' | tr '\n' ' ')"
    else
        echo "  Chrome/Chromium processes: None"
    fi
    
    if [ $firefox_procs -gt 0 ]; then
        echo -e "  ${YELLOW}Firefox processes:${NC} $firefox_procs running"
        echo "    PIDs: $(pgrep -f 'firefox' | tr '\n' ' ')"
    else
        echo "  Firefox processes: None"
    fi
}

check_temp_dirs() {
    echo "Checking for Chrome temp directories:"
    
    chrome_temps=$(find /tmp -name "chrome_test_*" -o -name ".com.google.Chrome.*" 2>/dev/null | wc -l)
    if [ $chrome_temps -gt 0 ]; then
        echo -e "  ${YELLOW}Found $chrome_temps Chrome temp directories${NC}"
        find /tmp -name "chrome_test_*" -o -name ".com.google.Chrome.*" 2>/dev/null | head -5
        if [ $chrome_temps -gt 5 ]; then
            echo "  ... and $(($chrome_temps - 5)) more"
        fi
    else
        echo "  No Chrome temp directories found"
    fi
}

check_selenium_grid() {
    echo -n "Checking Selenium Grid status... "
    
    if curl -s "http://localhost:4444/status" > /dev/null 2>&1; then
        echo -e "${GREEN}RUNNING${NC}"
        
        # Get node status
        status=$(curl -s "http://localhost:4444/status" 2>/dev/null)
        ready=$(echo "$status" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['value']['ready'])" 2>/dev/null || echo "unknown")
        nodes=$(echo "$status" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data['value']['nodes']))" 2>/dev/null || echo "unknown")
        
        echo "  Grid ready: $ready"
        echo "  Nodes: $nodes"
    else
        echo -e "${RED}NOT RUNNING${NC}"
        
        # Check if jar exists
        if [ -f "selenium-server.jar" ]; then
            echo "  Selenium server JAR found"
        else
            echo "  Selenium server JAR not found"
        fi
    fi
}

fix_chrome_issues() {
    echo ""
    echo "Attempting to fix Chrome issues..."
    
    # Kill Chrome processes
    echo -n "Killing Chrome processes... "
    pkill -f "chrome" || true
    pkill -f "chromium" || true
    sleep 2
    echo "Done"
    
    # Clean temp directories
    echo -n "Cleaning Chrome temp directories... "
    rm -rf /tmp/chrome_test_* 2>/dev/null || true
    rm -rf /tmp/.com.google.Chrome.* 2>/dev/null || true
    rm -rf ~/.config/chromium/Singleton* 2>/dev/null || true
    rm -rf ~/.config/google-chrome/Singleton* 2>/dev/null || true
    echo "Done"
    
    echo -e "${GREEN}Chrome cleanup completed${NC}"
}

test_selenium_connection() {
    echo ""
    echo "Testing Selenium Grid connection..."
    
    # Create a simple Python test
    cat > /tmp/selenium_test.py << 'EOF'
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def test_chrome():
    print("Testing Chrome connection...")
    try:
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--user-data-dir=/tmp/test_chrome_profile')
        
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=options
        )
        driver.get('http://localhost:4444/ui')
        print(f"  SUCCESS - Title: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"  FAILED - {str(e)}")
        return False

def test_firefox():
    print("Testing Firefox connection...")
    try:
        options = FirefoxOptions()
        options.add_argument('--headless')
        
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=options
        )
        driver.get('http://localhost:4444/ui')
        print(f"  SUCCESS - Title: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"  FAILED - {str(e)}")
        return False

if __name__ == "__main__":
    chrome_ok = test_chrome()
    firefox_ok = test_firefox()
    
    if chrome_ok or firefox_ok:
        print("\nAt least one browser is working correctly!")
        sys.exit(0)
    else:
        print("\nBoth browsers failed. Please check the diagnostic output above.")
        sys.exit(1)
EOF

    # Run the test
    if command -v python3 &> /dev/null; then
        python3 /tmp/selenium_test.py
    else
        echo -e "${RED}Python 3 not found${NC}"
    fi
    
    rm -f /tmp/selenium_test.py
}

# Main diagnostic flow
echo "=== System Checks ==="
check_java
check_browsers
check_drivers
echo ""

echo "=== Process Checks ==="
check_processes
check_temp_dirs
echo ""

echo "=== Selenium Grid Check ==="
check_selenium_grid
echo ""

# Ask if user wants to fix issues
if [ $chrome_procs -gt 0 ] || [ $chrome_temps -gt 0 ]; then
    echo -e "${YELLOW}Chrome issues detected.${NC}"
    read -p "Do you want to clean up Chrome processes and temp files? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        fix_chrome_issues
    fi
fi

# Test connection
read -p "Do you want to test Selenium Grid connection? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    test_selenium_connection
fi

echo ""
echo "Diagnostic complete!"