#!/bin/bash

# Selenium Grid Automated Test Runner for Coder Workspace
# This script sets up the environment and runs Selenium tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SELENIUM_GRID_URL="http://localhost:4444"
TEST_SCRIPT="selenium_test_suite.py"
LOG_DIR="test_logs"
VENV_DIR="selenium_test_env"

# Functions
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_selenium_grid() {
    print_status "Checking Selenium Grid status..."
    
    if curl -s "${SELENIUM_GRID_URL}/status" > /dev/null 2>&1; then
        print_status "Selenium Grid is running at ${SELENIUM_GRID_URL}"
        
        # Get Grid status details
        grid_status=$(curl -s "${SELENIUM_GRID_URL}/status" | python3 -m json.tool 2>/dev/null || echo "Unable to parse status")
        echo "Grid Status:"
        echo "$grid_status" | head -20
    else
        print_error "Selenium Grid is not accessible at ${SELENIUM_GRID_URL}"
        print_status "Attempting to start Selenium Grid..."
        
        # Check if Java is installed
        if ! command -v java &> /dev/null; then
            print_error "Java is not installed. Installing..."
            sudo apt-get update && sudo apt-get install -y openjdk-11-jre
        fi
        
        # Download Selenium Grid if not present
        if [ ! -f "selenium-server.jar" ]; then
            print_status "Downloading Selenium Grid..."
            wget -q https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.15.0/selenium-server-4.15.0.jar -O selenium-server.jar
        fi
        
        # Start Selenium Grid in standalone mode
        print_status "Starting Selenium Grid in standalone mode..."
        java -jar selenium-server.jar standalone --port 4444 > selenium-grid.log 2>&1 &
        GRID_PID=$!
        echo $GRID_PID > selenium-grid.pid
        
        # Wait for Grid to start
        sleep 10
        
        if curl -s "${SELENIUM_GRID_URL}/status" > /dev/null 2>&1; then
            print_status "Selenium Grid started successfully (PID: $GRID_PID)"
        else
            print_error "Failed to start Selenium Grid. Check selenium-grid.log for details"
            exit 1
        fi
    fi
}

setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv $VENV_DIR
    fi
    
    # Activate virtual environment
    source $VENV_DIR/bin/activate
    
    # Install required packages
    print_status "Installing required Python packages..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install selenium pytest unittest-xml-reporting > /dev/null 2>&1
    
    print_status "Python environment ready"
}

create_test_directories() {
    print_status "Creating test directories..."
    mkdir -p $LOG_DIR
    mkdir -p $LOG_DIR/screenshots
    mkdir -p $LOG_DIR/reports
}

run_tests() {
    local test_name=$1
    
    if [ -z "$test_name" ]; then
        print_status "Running all tests..."
    else
        print_status "Running test: $test_name"
    fi
    
    # Run the test suite
    if [ -f "$TEST_SCRIPT" ]; then
        python3 $TEST_SCRIPT --test "${test_name:-all}" --grid-url "${SELENIUM_GRID_URL}/wd/hub"
        TEST_EXIT_CODE=$?
    else
        print_error "Test script $TEST_SCRIPT not found!"
        exit 1
    fi
    
    return $TEST_EXIT_CODE
}

generate_summary_report() {
    print_status "Generating test summary..."
    
    # Find the latest JSON report
    latest_json=$(ls -t $LOG_DIR/test_results_*.json 2>/dev/null | head -1)
    
    if [ -n "$latest_json" ]; then
        echo ""
        echo "===== TEST SUMMARY ====="
        python3 -c "
import json
with open('$latest_json', 'r') as f:
    data = json.load(f)
    run = data['test_run']
    print(f'Total Tests: {run[\"total_tests\"]}')
    print(f'Passed: {run[\"passed\"]}')
    print(f'Failed: {run[\"failed\"]}')
    print(f'Errors: {run[\"errors\"]}')
    print(f'Skipped: {run[\"skipped\"]}')
    print(f'Success Rate: {(run[\"passed\"]/run[\"total_tests\"]*100) if run[\"total_tests\"] > 0 else 0:.1f}%')
"
        echo "========================"
        echo ""
        
        # Show failed tests
        if [ $(python3 -c "import json; data=json.load(open('$latest_json')); print(data['test_run']['failed'] + data['test_run']['errors'])") -gt 0 ]; then
            echo "Failed Tests:"
            python3 -c "
import json
with open('$latest_json', 'r') as f:
    data = json.load(f)
    for test in data['test_cases']:
        if test['status'] in ['FAIL', 'ERROR']:
            print(f\"  - {test['name']}: {test['status']} - {test.get('error_message', 'No error message')[:100]}...\")
"
            echo ""
        fi
    fi
    
    # Display report locations
    latest_html=$(ls -t $LOG_DIR/test_report_*.html 2>/dev/null | head -1)
    if [ -n "$latest_html" ]; then
        print_status "HTML Report: $latest_html"
    fi
    
    print_status "Log files: $LOG_DIR/"
}

cleanup() {
    print_status "Cleaning up..."
    
    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    
    # Stop Selenium Grid if we started it
    if [ -f "selenium-grid.pid" ]; then
        GRID_PID=$(cat selenium-grid.pid)
        if ps -p $GRID_PID > /dev/null 2>&1; then
            print_status "Stopping Selenium Grid (PID: $GRID_PID)..."
            kill $GRID_PID
            rm selenium-grid.pid
        fi
    fi
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    echo "======================================"
    echo "Selenium Grid Test Automation"
    echo "======================================"
    echo ""
    
    # Parse command line arguments
    TEST_NAME=""
    SKIP_SETUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test)
                TEST_NAME="$2"
                shift 2
                ;;
            --skip-setup)
                SKIP_SETUP=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --test NAME      Run specific test (default: all)"
                echo "  --skip-setup     Skip environment setup"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Setup steps
    if [ "$SKIP_SETUP" = false ]; then
        check_selenium_grid
        setup_python_environment
    else
        # Still activate venv if it exists
        if [ -d "$VENV_DIR" ]; then
            source $VENV_DIR/bin/activate
        fi
    fi
    
    create_test_directories
    
    # Run tests
    run_tests "$TEST_NAME"
    TEST_RESULT=$?
    
    # Generate reports
    generate_summary_report
    
    # Exit with test result code
    if [ $TEST_RESULT -eq 0 ]; then
        print_status "All tests passed successfully!"
    else
        print_error "Some tests failed. Check the reports for details."
    fi
    
    exit $TEST_RESULT
}

# Run main function
main "$@"