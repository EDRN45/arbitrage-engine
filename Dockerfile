FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Run the application
CMD ["python", "-u", "bfmr_monitor.py"]
