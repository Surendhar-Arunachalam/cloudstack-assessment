from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json
import pyotp
import os
import random

# Random delays for mimicking human behavior
short_delay = random.randint(2500, 5000)

# Function to fill login details on LinkedIn
def fill_details(page, USERNAME, PASSWORD):
    if page.locator("input#username").is_visible(timeout=5000):
        page.fill('input#username', USERNAME)
    page.fill('input#password', PASSWORD)
    page.wait_for_timeout(short_delay)
    page.click('button[type="submit"]')

# Function to create and store LinkedIn session cookies
def cookie_create(USERNAME, PASSWORD, MFA_KEY):
    try:
        with sync_playwright() as p:
            # Check if a user data directory exists
            dir_flag = 0
            if os.path.isdir(USERNAME):
                dir_flag = 1

            # Launch persistent browser context with stealth settings
            context = p.chromium.launch_persistent_context(
                user_data_dir=USERNAME,
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-default-browser-check",
                    "--disable-infobars",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--disable-background-networking",
                    "--mute-audio",
                    "--hide-scrollbars",
                ],
            )

            # Load default cookies if new directory
            if dir_flag == 0:
                for page in context.pages:
                    page.close()
                with open("default_cookies.json", "r") as dc:
                    default_cookies = json.load(dc)
                    context.add_cookies(default_cookies)

            page = context.pages[0] if context.pages else context.new_page()

            # Apply stealth to overcome challenges
            stealth_sync(page)

            # Set headers to mimic real browser
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })

            # Go to LinkedIn login page
            page.goto("https://www.linkedin.com/login", timeout=30000, wait_until="domcontentloaded")

            # Fill login form if on login page
            if page.url.startswith("https://www.linkedin.com/login"):
                page.wait_for_timeout(short_delay)
                fill_details(page, USERNAME, PASSWORD)

            # Fill login again if redirected to checkpoint login
            if page.url.startswith("https://www.linkedin.com/checkpoint/lg/login"):
                page.wait_for_timeout(short_delay)
                fill_details(page, USERNAME, PASSWORD)

            # Handle 2FA challenge if present
            if page.url.startswith("https://www.linkedin.com/checkpoint/challenge/"):
                print("Verification required.")
                page.wait_for_timeout(short_delay)
                try:
                    page.wait_for_selector('input[name="pin"]', timeout=5000)
                    page.wait_for_timeout(short_delay)
                    page.fill('input[name="pin"]', pyotp.TOTP(MFA_KEY).now())
                    page.click('button[type="submit"]')
                except Exception as e:
                    print("Verification error", e)
                    context.close()
                    return str(e).strip()
                page.wait_for_timeout(short_delay)
                page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000, wait_until='domcontentloaded')
                print("Logged in after verification")
            # If still stuck at login checkpoint
            elif page.url.startswith("https://www.linkedin.com/checkpoint/lg/login"):
                return "checkpoint error"
            # Logged in successfully without challenge
            else:
                page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000, wait_until='domcontentloaded')
                print("Logged in without challenge")

            # Get cookies from session
            cookies = context.cookies()
            cookie_str = '; '.join(f'{c["name"]}={c["value"]}' for c in cookies)
            csrf_token = '; '.join(c["value"].replace('"', '') for c in cookies if c["name"] == "JSESSIONID")

            # Load existing cookie file if exists
            if os.path.exists("cookies.json"):
                with open("cookies.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []

            # Update cookie if user exists, else add new
            found = False
            for data_iter in data:
                if data_iter['username'] == USERNAME:
                    data_iter["cookie"] = cookie_str
                    data_iter["csrf-token"] = csrf_token
                    found = True
                    break
            if not found:
                data.append({
                    "username": USERNAME,
                    "cookie": cookie_str,
                    "csrf-token": csrf_token
                })

            # Save updated cookie data
            with open("cookies.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            context.close()
        return "success"
    except Exception as e:
        # Return error message with details
        return "error: " + str(e).strip()

# if __name__ == "__main__":
#     USERNAME = "test@gmail.com"
#     PASSWORD = "test1234"
#     MFA_KEY = "ZZC6C6W563QK2FSH64FAHBURHTKX27CD"
