# Selenium Grid Testing in Coder Workspace

This repository contains a complete automated testing solution for running Selenium tests in your Coder workspace with comprehensive logging and reporting capabilities.

## Overview

The testing framework includes:
- Automated Selenium Grid setup and management
- Python-based test suite with unittest framework
- Comprehensive logging (console, file, JSON, HTML)
- Screenshot capture for failed tests
- Test result reporting and analytics
- Easy-to-use shell script for test execution

## Quick Start

1. **Start your Coder workspace** with the provided template

2. **Copy the test files** to your workspace:
   ```bash
   # Save the Python test suite as selenium_test_suite.py
   # Save the shell script as run_tests.sh
   chmod +x run_tests.sh
   ```

3. **Run the tests**:
   ```bash
   ./run_tests.sh
   ```

## Files Description

### 1. `selenium_test_suite.py`
The main Python test suite containing:
- Base test class with automatic setup/teardown
- Test result logging functionality
- Sample test cases for web applications
- HTML and JSON report generation

### 2. `run_tests.sh`
Automated test runner script that:
- Checks Selenium Grid status
- Sets up Python virtual environment
- Installs required dependencies
- Executes tests
- Generates summary reports

### 3. `Dockerfile` (optional)
Custom Docker image with pre-installed:
- Selenium Server
- Chrome and Firefox browsers
- Python testing dependencies
- Automated startup scripts

## Usage

### Running All Tests
```bash
./run_tests.sh
```

### Running Specific Test
```bash
./run_tests.sh --test test_google_search
```

### Skip Setup (if already configured)
```bash
./run_tests.sh --skip-setup
```

### Available Test Methods
- `test_google_search` - Tests Google search functionality
- `test_coder_website` - Tests Coder.com website loading
- `test_github_coder_repo` - Tests GitHub repository page
- `test_selenium_grid_console` - Tests Grid console accessibility

## Test Results and Logging

### Log Directory Structure
```
test_logs/
├── selenium_tests_YYYYMMDD_HHMMSS.log  # Detailed test logs
├── test_results_YYYYMMDD_HHMMSS.json   # JSON test results
├── test_report_YYYYMMDD_HHMMSS.html    # HTML test report
└── screenshots/                         # Failed test screenshots
    └── test_name_YYYYMMDD_HHMMSS.png
```

### Log Formats

1. **Console Output**: Real-time test execution status
2. **Log File**: Detailed debug information with timestamps
3. **JSON Report**: Structured test results for programmatic access
4. **HTML Report**: Visual test report with screenshots

### Sample JSON Report Structure
```json
{
  "test_run": {
    "timestamp": "20240105_143022",
    "start_time": "2024-01-05T14:30:22.123456",
    "end_time": "2024-01-05T14:31:45.789012",
    "total_tests": 4,
    "passed": 3,
    "failed": 1,
    "errors": 0,
    "skipped": 0
  },
  "test_cases": [
    {
      "name": "test_google_search",
      "status": "PASS",
      "duration": 5.23,
      "error_message": null,
      "screenshot": null
    }
  ]
}
```

## Adding New Tests

To add new tests, create a new test method in the `WebApplicationTests` class:

```python
def test_my_application(self):
    """Test description"""
    self.driver.get("https://myapp.com")
    
    # Wait for element
    element = WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.ID, "my-element"))
    )
    
    # Perform assertions
    self.assertEqual(element.text, "Expected Text")
    
    # Log information
    self.logger.info("Test passed successfully")
```

## Selenium Grid Management

### Check Grid Status
```bash
curl http://localhost:4444/status | python3 -m json.tool
```

### View Grid Console
Open in browser: `http://localhost:4444/ui`

### Manual Grid Start
```bash
java -jar selenium-server.jar standalone --port 4444
```

## Troubleshooting

### Common Issues

1. **Selenium Grid not accessible**
   - Check if port 4444 is available
   - Verify Java is installed: `java -version`
   - Check Grid logs: `tail -f selenium-grid.log`

2. **Tests failing with timeout**
   - Increase wait times in test code
   - Check if Grid has available nodes
   - Verify browser drivers are installed

3. **Screenshot capture fails**
   - Ensure screenshots directory exists
   - Check disk space
   - Verify driver is still active

### Debug Mode

Enable verbose logging by modifying the test script:
```python
logging.getLogger('selenium').setLevel(logging.DEBUG)
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Selenium Tests
  run: |
    ./run_tests.sh
  continue-on-error: true
    
- name: Upload Test Results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test_logs/
```

### Jenkins Pipeline Example
```groovy
stage('Run Selenium Tests') {
    steps {
        sh './run_tests.sh'
    }
    post {
        always {
            archiveArtifacts artifacts: 'test_logs/**/*'
            publishHTML([
                reportDir: 'test_logs',
                reportFiles: 'test_report_*.html',
                reportName: 'Selenium Test Report'
            ])
        }
    }
}
```

## Performance Tips

1. **Run tests in parallel**:
   ```python
   # Use pytest-xdist
   pytest -n 4 selenium_test_suite.py
   ```

2. **Reuse browser sessions** for related tests
3. **Use explicit waits** instead of implicit waits
4. **Run headless** for faster execution
5. **Cache downloaded files** and drivers

## Security Considerations

- Never commit sensitive data in test scripts
- Use environment variables for credentials
- Sanitize screenshots before sharing
- Review test logs for sensitive information

## Contributing

To contribute new tests or improvements:
1. Add test methods following the existing pattern
2. Ensure proper error handling
3. Include meaningful log messages
4. Update documentation

## License

This testing framework is provided as-is for use with Coder workspaces.