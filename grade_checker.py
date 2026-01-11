import os
import sys
import requests
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION --- 
USERNAME = os.getenv("HSBI_USER")
PASSWORD = os.getenv("HSBI_PASS")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "last_grade_count.txt"
LOGIN_URL = "https://www.hsbi.de/qisserver/rds?state=user&type=0"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram: {e}")

def get_grade_data():
    with sync_playwright() as p:
        # Launch with a realistic User-Agent to bypass bot detection
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        try:
            print(f"Navigating to: {LOGIN_URL}")
            # Wait until the basic page structure is loaded
            page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
            
            # --- MANDATORY FIRST LOOK SCREENSHOT ---
            # This shows us exactly what the bot sees first (Cookie banners, etc.)
            page.wait_for_timeout(5000) 
            page.screenshot(path="first_view.png")
            print("Captured first_view.png - Checking for login fields...")

            # Use smart selectors to find 'asdf' or any username field
            username_field = page.locator('input[name="asdf"]')
            username_field.wait_for(state="visible", timeout=20000)
            
            print("Entering credentials...")
            username_field.fill(USERNAME)
            page.fill('input[name="fdsa"]', PASSWORD)
            
            # Use the specific button ID from your screenshot
            print("Submitting login...")
            page.click('button[id="loginForm:login"]')
            page.wait_for_load_state("networkidle")

            # Navigation to Notenspiegel
            print("Navigating to Prüfungsverwaltung...")
            page.get_by_role("link", name="Prüfungsverwaltung").click()
            page.wait_for_load_state("networkidle")
            
            print("Navigating to Notenspiegel...")
            page.get_by_role("link", name="Notenspiegel").click()
            page.wait_for_load_state("networkidle")
            
            # Using the exact title from your blue 'i' icon screenshot
            print("Opening grade details...")
            page.locator('a[title="Leistungen für Abschluss BA Bachelor anzeigen"]').click()

            # Final Wait for Table
            page.wait_for_selector('table', timeout=30000)
            print("Grades found!")
            
            content = page.content()
            return content

        except Exception as e:
            # Save the visual state of the failure for debugging
            page.screenshot(path="debug_error.png")
            print(f"Scraper Error: {e}")
            raise e
        finally:
            browser.close()

def parse_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Count rows using your specific class
    exam_names = []
    for row in soup.find_all('tr'):
        cols = row.find_all('td', class_='tabelle1_alignleft')
        if len(cols) >= 2:
            name = cols[1].get_text(strip=True)
            if "Durchschnittsnote" not in name:
                exam_names.append(name)
    return len(exam_names)

def main():
    if not USERNAME or not PASSWORD:
        print("Error: HSBI credentials not set.")
        sys.exit(1)

    try:
        html = get_grade_data()
        current_count = parse_count(html)
        print(f"Current exam count: {current_count}")

        last_count = 0
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                last_count = int(f.read().strip())

        if current_count > last_count:
            diff = current_count - last_count
            send_telegram(f"🎓 HSBI ALERT: {diff} new result(s) added!\nTotal exams: {current_count}")
            with open(DATA_FILE, "w") as f:
                f.write(str(current_count))
        else:
            print("No new results found.")

    except Exception as e:
        print(f"Script failed: {e}")

if __name__ == "__main__":
    main()