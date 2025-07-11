
## 🔗 LinkedIn Connections Scraper API

A Python-based API service that logs into LinkedIn using Playwright, handles 2FA, persists session cookies, and fetches connection details using LinkedIn's internal Voyager APIs.


## 🚀 Features

- Login to LinkedIn using given credentials
- Session persistence using saved browser cookies
- Handles 2FA (single-use code) manually in browser
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
├── cookies.json           # Stored LinkedIn session cookies
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
| `session_persistence` | ✅     | `True` to reuse cookies, `False` to login fresh     |

#### 🔸 Example Request

```bash
curl -X POST http://localhost:5000/linkedin/connections   -F "username=test@example.com"   -F "password=dGVzdHBhc3M="   -F "session_persistence=False"
```

#### 🔸 Example Response

```json
{
    "data": [
        {
            "logged_in_user": "Surendhar Arunachalam"
        },
        {
            "headline": "Software Developer | Freelancer | Trainer.",
            "name": "Anjnee K. Sharma is open to work",
            "url": "https://www.linkedin.com/in/anjneekumarsharma"
        },
        {
            "headline": "Data Analyst at Pivotree",
            "name": "Aravind D is open to work",
            "url": "https://www.linkedin.com/in/aravind-d-9b613097"
        },
        {
            "headline": "Data enthusiast",
            "name": "Arulanand R",
            "url": "https://www.linkedin.com/in/arulanand-r"
        }
	],
    "message": "Connections fetched successfully.",
    "status": "success"
}		
```

---

## 🛡️ Anti-Bot Techniques Used

- Uses real browser session via Playwright
- Uses count as 100 in requests params for pagination reduces the risk of getting blocked
- Saves session cookies to avoid frequent logins
- Sets headers (e.g. `user-agent`) to mimic browser
- Uses Voyager API, avoiding scraping HTML
