import os
import time
import random
import requests
import sys
import json
import threading
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

# Force UTF-8 encoding for stdout/stderr to handle emojis on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
STATUS_FILE = "last_status.txt"
MONITORS_FILE = "monitors.json"
FAILURE_THRESHOLD = 3

# Global state for status reporting
current_monitors_status = {}
last_check_time = "Never"
is_active = True

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def load_monitors():
    try:
        if os.path.exists(MONITORS_FILE):
            with open(MONITORS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        log("monitors.json not found.")
        return []
    except Exception as e:
        log(f"Error loading monitors: {e}")
        return []

def send_telegram_message(message, chat_id=TELEGRAM_CHAT_ID):
    if not TELEGRAM_TOKEN or not chat_id:
        log("Telegram token or chat ID missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        log(f"Telegram message sent to {chat_id}")
    except Exception as e:
        log(f"Failed to send Telegram message: {e}")

def handle_telegram_updates():
    """Polls for Telegram updates and handles commands like /status and /stop"""
    global is_active
    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    log("Starting Telegram polling thread...")
    
    while is_active:
        try:
            params = {"offset": offset, "timeout": 30}
            response = requests.get(url, params=params, timeout=40)
            data = response.json()
            
            if data.get("ok"):
                for result in data.get("result", []):
                    offset = result["update_id"] + 1
                    message = result.get("message", {})
                    text = message.get("text", "").strip()
                    chat_id = message.get("chat", {}).get("id")
                    
                    # Security Check
                    if str(chat_id) != str(TELEGRAM_CHAT_ID):
                        log(f"⚠️ Security: Ignored command '{text}' from unauthorized chat_id {chat_id}")
                        continue
                    
                    if text == "/status":
                        log(f"Received /status command from {chat_id}")
                        
                        # Build status message
                        msg = "🤖 **Arbitrage Engine Status**\n"
                        msg += "✅ Active\n"
                        msg += f"🕒 Last Check: {last_check_time}\n\n"
                        msg += "📊 **Monitored Items:**\n"
                        
                        monitors = load_monitors()
                        if not monitors:
                            msg += "No monitors configured."
                        else:
                            for mon in monitors:
                                name = mon.get("name", "Unknown")
                                short_name = (name[:30] + '..') if len(name) > 30 else name
                                status = current_monitors_status.get(mon.get("url"), "Pending")
                                msg += f"- {short_name}\n  Status: {status}\n"
                        
                        send_telegram_message(msg, chat_id)
                        
                    elif text == "/stop":
                        log(f"Received /stop command from {chat_id}")
                        send_telegram_message("🛑 Shutting down monitoring engine...", chat_id)
                        is_active = False
                        log("Exit signal received. Terminating process.")
                        # We let the main loop break instead of forced exit if possible, 
                        # but os._exit is safer to kill threads
                        os._exit(0)
                        
            time.sleep(1)
            
        except Exception as e:
            if is_active:
                log(f"Telegram polling error: {e}")
                time.sleep(5)

def check_stock_and_price(url, site, page):
    if not url:
        return 0.0, False
        
    try:
        log(f"Checking {url}...")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        content = page.content().lower()
        price = 0.0
        in_stock = False
        
        # Site-specific logic (Refine this with real selectors)
        if site == "amazon":
            if "currently unavailable" not in content and "out of stock" not in content:
                in_stock = True
                # Placeholder for price parsing
                price = 0.0 
        elif site == "bestbuy":
            if "sold out" not in content and "unavailable" not in content:
                in_stock = True
                price = 0.0
        else:
            # Generic fallback
            in_stock = "out of stock" not in content
        
        return price, in_stock
    except Exception as e:
        log(f"Error checking {url}: {e}")
        return None, False

def load_last_status_map():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_last_status_map(status_map):
    try:
        with open(STATUS_FILE, "w") as f:
            json.dump(status_map, f)
    except Exception as e:
        log(f"Failed to save status file: {e}")

def main():
    global last_check_time
    
    # Start Telegram polling in background
    t_thread = threading.Thread(target=handle_telegram_updates, daemon=True)
    t_thread.start()
    
    monitors = load_monitors()
    log(f"Loaded {len(monitors)} monitors.")
    
    last_status_map = load_last_status_map()
    
    # If no monitors, just wait for Telegram updates (or config update)
    if not monitors:
        log("No monitors found. Waiting for config update...")
        while not monitors and is_active:
            time.sleep(10)
            monitors = load_monitors()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ua = UserAgent()
        
        while is_active:
            try:
                monitors = load_monitors() # Reload config dynamically
                context = browser.new_context(user_agent=ua.random)
                page = context.new_page()
                
                last_check_time = datetime.now().strftime("%H:%M:%S")
                
                for item in monitors:
                    if not is_active: break
                    
                    url = item.get("url")
                    if not url:
                        continue
                        
                    target = item.get("target_payout", 0)
                    site = item.get("site", "unknown")
                    name = item.get("name", "Unknown")
                    
                    price, in_stock = check_stock_and_price(url, site, page)
                    
                    status_text = f"Stock: {in_stock}, Price: {price}"
                    current_monitors_status[url] = status_text
                    log(f"[{name[:10]}] {status_text}")
                    
                    # Alert Logic
                    item_last_status = last_status_map.get(url, "NO_DEAL")
                    current_token = f"IN_STOCK_{price}" if in_stock else "NO_DEAL"
                    
                    if in_stock and current_token != item_last_status:
                         msg = f"🚨 DEAL ALERT! \n\nItem: {name}\nPrice: ${price}\nTarget: ${target}\nLink: {url}"
                         send_telegram_message(msg)
                         last_status_map[url] = current_token
                         save_last_status_map(last_status_map)
                    elif not in_stock and item_last_status != "NO_DEAL":
                         last_status_map[url] = "NO_DEAL"
                         save_last_status_map(last_status_map)
                    
                    # Random delay between items to be safe
                    time.sleep(random.randint(5, 10))
                
                context.close()
                
                if is_active:
                    sleep_time = random.randint(300, 600) # 5-10 mins
                    log(f"Cycle complete. Sleeping for {sleep_time}s...")
                    time.sleep(sleep_time)
                
            except Exception as e:
                log(f"Main loop error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    main()
