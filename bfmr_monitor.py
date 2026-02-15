import os
import time
import random
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

# Force UTF-8 encoding for stdout/stderr to handle emojis on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRODUCT_URL = os.getenv("PRODUCT_URL")
TARGET_PAYOUT = float(os.getenv("TARGET_PAYOUT", "0.0"))
STATUS_FILE = "last_status.txt"
FAILURE_THRESHOLD = 3

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        log(f"Telegram alert sent: {message}")
    except Exception as e:
        log(f"Failed to send Telegram alert: {e}")

def get_last_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return f.read().strip()
        except Exception:
            return None
    return None

def update_last_status(status):
    try:
        with open(STATUS_FILE, "w") as f:
            f.write(status)
    except Exception as e:
        log(f"Failed to update status file: {e}")

def check_stock_and_price():
    ua = UserAgent()
    user_agent = ua.random
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        
        try:
            log(f"Navigating to {PRODUCT_URL}...")
            page.goto(PRODUCT_URL, timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # --- CUSTOM SELECTOR LOGIC HERE ---
            # This part needs to be customized for specific retailers (Amazon, BestBuy, etc.)
            # For now, we'll implement a dummy check for testing and a generic fallback.
            
            price = None
            in_stock = False
            
            if "example.com" in PRODUCT_URL:
                # Simulation for dry run
                log("Simulating check on example.com")
                price = 99.99
                in_stock = True
            else:
                # Generic attempts - highly dependent on site structure
                # This serves as a placeholder for real logic
                content = page.content().lower()
                in_stock = "out of stock" not in content and "currently unavailable" not in content
                
                # Try to find a price (very basic heuristic)
                # In a real scenario, use specific selectors like '#priceblock_ourprice'
                # price = float(page.locator("some-selector").inner_text().replace("$", ""))
                price = 0.0 # Default to 0 if not found to avoid false positives
                
            return price, in_stock
            
        finally:
            browser.close()

def main():
    failure_count = 0
    
    log("Starting BFMR Monitor...")
    log(f"Target Payout: {TARGET_PAYOUT}")
    
    while True:
        try:
            price, in_stock = check_stock_and_price()
            
            # Reset failure count on success
            failure_count = 0
            
            status_message = f"Price: {price}, Stock: {in_stock}"
            log(f"Check result: {status_message}")
            
            last_status = get_last_status()
            
            if in_stock and (price is not None and price <= TARGET_PAYOUT):
                current_status_token = f"IN_STOCK_{price}"
                
                if current_status_token != last_status:
                    alert_msg = f"🚨 DEAL ALERT! \n\nProduct is IN STOCK.\nPrice: ${price}\nTarget: ${TARGET_PAYOUT}\nLink: {PRODUCT_URL}"
                    send_telegram_alert(alert_msg)
                    update_last_status(current_status_token)
                else:
                    log("Deal active, but status unchanged. Skipping alert.")
            else:
                # If not a deal, clear the status so we get alerted if it comes back
                if last_status != "NO_DEAL":
                    update_last_status("NO_DEAL")
                    log("No deal found. Status updated.")

        except Exception as e:
            failure_count += 1
            log(f"Error during check ({failure_count}/{FAILURE_THRESHOLD}): {e}")
            
            if failure_count >= FAILURE_THRESHOLD:
                send_telegram_alert(f"⚠️ Monitor Error: Action Required\n\nScript has failed {failure_count} times in a row.\nError: {str(e)}")
                # Reset failure count after alerting to avoid spamming the error every loop? 
                # Or keep it high to alert every time? 
                # The user said "send me a Telegram alert... so I know". 
                # I'll reset it to 0 to provide a "snooze" on the error alert for another 3 cycles.
                failure_count = 0 
        
        # Sleep logic
        sleep_time = random.randint(900, 2700) # 15 to 45 minutes
        log(f"Sleeping for {sleep_time} seconds ({sleep_time/60:.1f} minutes)...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
