# Dockerfile for Coder Workspace with Selenium Testing
FROM codercom/enterprise-base:ubuntu

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    openjdk-11-jre \
    wget \
    curl \
    python3-pip \
    python3-venv \
    chromium-browser \
    chromium-chromedriver \
    firefox \
    firefox-geckodriver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Download Selenium Server
RUN wget -q https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.15.0/selenium-server-4.15.0.jar -O /opt/selenium-server.jar

# Create directories for tests
RUN mkdir -p /home/coder/selenium-tests/test_logs \
    && mkdir -p /home/coder/selenium-tests/test_logs/screenshots \
    && mkdir -p /home/coder/selenium-tests/test_logs/reports \
    && chown -R coder:coder /home/coder/selenium-tests

# Switch back to coder user
USER coder
WORKDIR /home/coder

# Create Python virtual environment and install packages
RUN python3 -m venv /home/coder/selenium_test_env \
    && /home/coder/selenium_test_env/bin/pip install --upgrade pip \
    && /home/coder/selenium_test_env/bin/pip install \
        selenium==4.15.0 \
        pytest==7.4.3 \
        pytest-html==4.1.1 \
        pytest-xdist==3.3.1 \
        unittest-xml-reporting==3.2.0 \
        requests==2.31.0

# Create a startup script for Selenium Grid
RUN echo '#!/bin/bash\n\
echo "Starting Selenium Grid..."\n\
java -jar /opt/selenium-server.jar standalone \
  --port 4444 \
  --enable-managed-downloads true \
  --selenium-manager true \
  > /home/coder/selenium-grid.log 2>&1 &\n\
echo $! > /home/coder/selenium-grid.pid\n\
echo "Selenium Grid started with PID $(cat /home/coder/selenium-grid.pid)"\n\
echo "Waiting for Grid to be ready..."\n\
sleep 10\n\
curl -s http://localhost:4444/status | python3 -m json.tool || echo "Grid status check failed"' \
> /home/coder/start-selenium-grid.sh && chmod +x /home/coder/start-selenium-grid.sh

# Create a health check script
RUN echo '#!/bin/bash\n\
if curl -s http://localhost:4444/status > /dev/null 2>&1; then\n\
    echo "Selenium Grid is healthy"\n\
    exit 0\n\
else\n\
    echo "Selenium Grid is not responding"\n\
    exit 1\n\
fi' > /home/coder/check-selenium-health.sh && chmod +x /home/coder/check-selenium-health.sh

# Set environment variables
ENV SELENIUM_GRID_URL=http://localhost:4444
ENV PATH="/home/coder/selenium_test_env/bin:${PATH}"

# Default command
CMD ["/bin/bash"]