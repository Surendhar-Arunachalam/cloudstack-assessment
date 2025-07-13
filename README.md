
## 🔗 LinkedIn Connections Scraper using Voyager API

A Python-based API service that logs into LinkedIn using Playwright, handles 2FA, persists session cookies, and fetches connection details using LinkedIn's internal Voyager APIs.


## 🚀 Features

- Login to LinkedIn using given credentials
- Session persistence using saved browser cookies
- Handles 2FA (single-use code) programatically
- Uses **LinkedIn's Voyager API** to fetch data
- Returns paginated connection data as JSON
- Simple Flask API interface
- Provides a script to test the API functionality

---

## 🏗️ Project Structure

```
linkedin_scraper/
├── linkedin_api.py        # Flask API server with requests and parser
├── linkedin_login.py      # Playwright-based login with 2FA support
├── default_cookies.json   # Stored LinkedIn Home page cookies 
├── cookies.json           # To Store LinkedIn session cookies
├── requirements.txt       # Project dependencies
└── README.md              # You are here!
```

---

## ⚙️ Setup Instructions

### 1. 🔧 Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```


### 2. ▶️ Run Flask Server

```bash
python linkedin_api.py
```

The API will be available at `http://127.0.0.1:5000/linkedin/connections`

---

## 📡 API Endpoint

### POST `/linkedin/connections`

Logs in to LinkedIn, fetches the user's connections, and returns them as JSON.


#### 🔸 Form Data Parameters

| Field               | Required | Description                                         |
|--------------------|----------|-----------------------------------------------------|
| `username`         | ✅        | Your LinkedIn email address                         |
| `password`         | ✅        | Your LinkedIn password                             |
| `mfa_key` | ✅     | `Mandatory`  for 2FA enabled accounts else `None`    |

#### 🔸 Example Request

```bash
curl -X POST http://localhost:5000/linkedin/connections   -F "username=test@example.com"   -F "password=dGVzdHBhc3M="   -F "mfa_key=ZZC6C6W563QK2FSH64FAHBURHTKX27CD"
```

#### 🔸 Example Response

```json
{
  "account_logged_in_user": "test@gmail.com",
  "data": [
    {
      "headline": "Senior Software Engineer at WorldatWork | ASP.Net Core, Azure, MVC, Web API, Linux",
      "name": "Karthikeyan T V",
      "url": "https://www.linkedin.com/in/karthikeyantv"
    },
    {
      "headline": "eG Innovations",
      "name": "Venkatesan V C",
      "url": "https://www.linkedin.com/in/venkatchandran"
    },
    {
      "headline": "Proprietor at PIXXEL PRINT SOLUTIONS",
      "name": "Vignesh Krishnamoorthy",
      "url": "https://www.linkedin.com/in/vignesh-krishnamoorthy-6125b376"
    }
  ],
  "message": "Connections fetched successfully.",
  "status": "success"
}		
```

## 🧾 Field Descriptions
| Field                    | Type   | Description                                                           |
| ------------------------ | ------ | --------------------------------------------------------------------- |
| `account_logged_in_user` | string | The email/username of the account used to fetch LinkedIn connections. |
| `data`                   | array  | A list of LinkedIn connection profiles. Each item contains:           |
| → `name`                 | string | Full name of the connection.                                          |
| → `headline`             | string | Job title, current role, or professional summary from LinkedIn.       |
| → `url`                  | string | Public LinkedIn profile URL of the connection.                        |
| `message`                | string | Descriptive message about the response status.                        |
| `status`                 | string | `"success"` if request was successful; otherwise could be `"error"`.  |

---

## 🛡️Anti-Bot & Session Management Techniques Usedd

- Uses real browser session via Playwright
- Applies stealth settings to try to avoid bot detection
- Uses count as **`100`** in request params for pagination. Fetches maximum allowed connections per call, reducing request frequency and risk of blocks
- Uses LinkedIn's Voyager API instead of html
- Sets custom headers (e.g. `user-agent`)
- Saves session cookies to avoid frequent logins
- Uses `default_cookies.json` for fresh logins. Injects preloaded LinkedIn cookies during first-time login to reduce initial security challenges like captchas
- Reuses existing browser session (via launch_persistent_context). Automatically logs in to an existing user profile if session is still valid; reauthenticates only if needed
- Stores all logged-in users' cookies in `cookies.json`. Maintains cookie string, CSRF token, and username for each user, allowing quick reuse and easy session management

---

## ⚠️ Disclaimer
This project is for educational and research purposes only.
Do not use it to violate LinkedIn's User Agreement or for any unauthorized activity.

The developer is not responsible for misuse. Use only on your own account or in a test environment.
