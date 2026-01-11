import os
import sys
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION (via Environment Variables) --- 
USERNAME = os.getenv("HSBI_USER")
PASSWORD = os.getenv("HSBI_PASS")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "last_grade_count.txt"
LOGIN_URL = "https://www.hsbi.de/qisserver/rds?state=user&type=0"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing, skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram: {e}")

def get_grade_data():
    with sync_playwright() as p:
        # 1. Use a very specific browser launch to look human
        browser = p.chromium.launch(headless=True)
        # We add extra arguments to bypass common bot detection
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        try:
            print(f"Navigating to: {LOGIN_URL}")
            # Increase timeout and wait for the page to be completely still
            page.goto(LOGIN_URL, wait_until="commit", timeout=60000)
            
            # Wait a few seconds for any redirects or "Please wait" screens to finish
            page.wait_for_timeout(5000) 

            # Check if we are on the right page
            print(f"Current URL after load: {page.url}")

            # 2. Robust Credential Entry
            # We look for the 'asdf' field but handle the case where it's not there
            username_field = page.locator('input[name="asdf"]')
            username_field.wait_for(state="visible", timeout=20000)
            
            print("Entering credentials...")
            username_field.fill(USERNAME)
            page.fill('input[name="fdsa"]', PASSWORD)
            
            # 3. Submit
            print("Submitting login...")
            page.click('button[id="loginForm:login"]')
            page.wait_for_load_state("networkidle")

            # 4. Navigation (Based on your screenshots)
            print("Navigating to Prüfungsverwaltung...")
            # We use 'link' name matching which is very reliable in Playwright
            page.get_by_role("link", name="Prüfungsverwaltung").click()
            
            print("Navigating to Notenspiegel...")
            page.get_by_role("link", name="Notenspiegel").click()
            
            # 5. Click the info icon (The little blue 'i')
            print("Opening grade details...")
            # Using the exact title from your screenshot
            page.locator('a[title="Leistungen für Abschluss BA Bachelor anzeigen"]').click()

            # 6. Final Wait for Table
            page.wait_for_selector('table', timeout=20000)
            print("Grades found!")
            
            content = page.content()
            browser.close()
            return content

        except Exception as e:
            # This is key: it saves exactly what the bot saw so you can view it in GitHub
            page.screenshot(path="debug_error.png")
            print(f"Detailed Error: {e}")
            browser.close()
            raise e

def parse_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    # We target the rows in the results table
    # Your HTML uses 'tabelle1_alignleft' for exam names
    rows = soup.find_all('td', class_='tabelle1_alignleft')
    
    # Filter for exam titles (avoiding IDs or dates)
    # Based on your HTML, the exam text is in the 2nd column of each row
    exam_names = []
    for row in soup.find_all('tr'):
        cols = row.find_all('td', class_='tabelle1_alignleft')
        if len(cols) >= 2:
            name = cols[1].get_text(strip=True)
            if "Durchschnittsnote" not in name:
                exam_names.append(name)
    
    return len(exam_names), exam_names

def main():
    if not USERNAME or not PASSWORD:
        print("Error: HSBI credentials not set in environment variables.")
        sys.exit(1)

    try:
        html = get_grade_data()
        current_count, exams = parse_count(html)
        print(f"Current exam count: {current_count}")

        # Load last count
        last_count = 0
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                last_count = int(f.read().strip())

        # Logic for notification
        if current_count > last_count:
            diff = current_count - last_count
            msg = f"🎓 HSBI ALERT: {diff} new result(s) added!\nTotal exams: {current_count}"
            print(msg)
            send_telegram(msg)
            
            # Save new count
            with open(DATA_FILE, "w") as f:
                f.write(str(current_count))
        else:
            print("No new results found.")

    except Exception as e:
        error_msg = f"Scraper Error: {str(e)}"
        print(error_msg)
        # Uncomment the next line if you want to be notified of errors
        # send_telegram(error_msg)

if __name__ == "__main__":
    main()