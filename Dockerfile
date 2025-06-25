FROM nodered/node-red:3.1.10-18

# Switch to root to install system packages
USER root

# Install Python and basic dependencies (Alpine Linux)
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    chromium \
    chromium-chromedriver \
    wget \
    curl \
    unzip

# Install Python packages for scraping
COPY scrapers/requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

# Install Node-RED packages
RUN npm install \
    node-red-dashboard \
    node-red-node-email \
    node-red-node-ui-table \
    node-red-contrib-postgresql

# Create scrapers directory and copy files (not in /data which is mounted)
RUN mkdir -p /opt/scrapers
COPY scrapers/ /opt/scrapers/
RUN chmod +x /opt/scrapers/*.py && ls -la /opt/scrapers/

# Ensure all Python files are executable and have proper imports
RUN cd /opt/scrapers && python3 -c "import sys; print('Python path:', sys.path)"

# Set Chrome binary path for Selenium
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROME_PATH=/usr/lib/chromium/

# Switch back to node-red user
USER node-red
