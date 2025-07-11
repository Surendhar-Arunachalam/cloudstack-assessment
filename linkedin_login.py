from playwright.sync_api import sync_playwright
import json


def cookie_create(USERNAME, PASSWORD):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            ## For session persistent within browser
            # user_data_dir = "linkedin_profile"
            # context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
            # page = context.new_page()

            # Go to LinkedIn login page
            try:
                page.goto("https://www.linkedin.com/login", timeout=20000)
            except Exception as e:
                print("Timeout error, Pass.")

            # Enter credentials and log in
            if page.url.startswith("https://www.linkedin.com/login"):
                page.fill('input#username', USERNAME)
                page.fill('input#password', PASSWORD)
                page.wait_for_timeout(2500)
                page.click('button[type="submit"]')
                # Wait for successful login

            # Attempt re-login
            if page.url.startswith("https://www.linkedin.com/checkpoint/lg/login"):
                page.fill('input#username', USERNAME)
                page.fill('input#password', PASSWORD)
                page.wait_for_timeout(2500)
                page.click('button[type="submit"]')


            # Wait for 2FA or single-code or challenge
            if page.url.startswith("https://www.linkedin.com/checkpoint/challenge/"):
                print("Verification required.")
                print("Please enter the signin code in the browser")
                page.wait_for_timeout(5000)
                try:
                    page.wait_for_selector('input[name="pin"]', timeout=5000)
                except Exception as e:
                    print("Timed out waiting for verification code input")
                    context.close()
                    return str(e).strip()
                page.wait_for_timeout(5000)
                # After manual code entry, wait for successful navigation
                page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000)
                print("Logged in after verification")
            else:
                # Logged-in without challenge
                page.wait_for_url("https://www.linkedin.com/feed/", timeout=30000, wait_until='domcontentloaded')
                print("Logged in without challenge")

            # To get current profile
            profile_name = page.locator('h3.profile-card-name').inner_text()

            # Get and export cookies
            cookies = context.cookies()
            cookies.append({"name": "profile", "value": profile_name})
            with open("cookies.json", "w", encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            print("Cookies saved to cookies.json")
            context.close()
        return profile_name
    except Exception as e:
        print(e)
        return None


# if __name__ == "__main__":
#     USERNAME = "test@gmail.com"
#     PASSWORD = "test1234"
#     cookie_create(USERNAME, PASSWORD)
