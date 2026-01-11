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
        # Launching Chromium
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to HSBI Login...")
        page.goto(LOGIN_URL)
        
        # LSF portals often use 'asdf' and 'fdsa' for login fields
        page.fill('input[name="asdf"]', USERNAME)
        page.fill('input[name="fdsa"]', PASSWORD)
        page.click('button[name="login"], input[type="submit"]')
        
        # Wait for login to complete (looking for logout link)
        page.wait_for_selector('a[href*="logout"]')

        # Navigation steps based on your HTML structure
        print("Navigating to Notenspiegel...")
        page.get_by_role("link", name="Prüfungsverwaltung").click()
        page.get_by_role("link", name="Notenspiegel").click()
        
        # Click the info icon for [BA] Bachelor
        # This matches the 'i' icon next to your degree
        page.locator('a[title^="Leistungen für Abschluss [BA]"]').click()

        # Wait for the results table
        page.wait_for_selector('table')
        content = page.content()
        browser.close()
        return content

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