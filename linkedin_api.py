import json
import requests
import urllib3
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from flask import Flask, request, jsonify
from linkedin_login import cookie_create


app = Flask(__name__)
BASE_URL = "https://www.linkedin.com/voyager/api/relationships/dash/connections"


# Load cookies for given username
def load_cookies(username_input):
    cookie_file = 'cookies.json'
    cookie_str = csrf_token = username = None

    # Create empty cookie file if not exists
    if not os.path.exists(cookie_file):
        with open(cookie_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
            return cookie_str, csrf_token, username

    # Read and find matching user cookie
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            for cookie_iter in cookies:
                if cookie_iter['username'] == username_input:
                    cookie_str = cookie_iter['cookie']
                    csrf_token = cookie_iter['csrf-token']
                    username = cookie_iter['username']
                    break
    except Exception as e:
        print(e)
    return cookie_str, csrf_token, username


# Return standard LinkedIn headers
def get_headers():
    return {
        'accept': 'application/vnd.linkedin.normalized+json+2.1', 'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.linkedin.com/mynetwork/invite-connect/connections/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'x-li-lang': 'en_US',
        'x-li-page-instance': 'urn:li:page:d_flagship3_search_srp_people;uEug9A5yRiaqxVIuxUd3lQ==',
        'x-li-pem-metadata': 'Voyager - People SRP=search-results',
        'x-li-track': '{"clientVersion":"1.13.36933","mpVersion":"1.13.36933","osName":"web","timezoneOffset":5.5,"timezone":"Asia/Calcutta","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1.125,"displayWidth":1728,"displayHeight":972}',
        'x-restli-protocol-version': '2.0.0',
    }


# API endpoint to get LinkedIn connections
@app.route("/linkedin/connections", methods=["POST"])
def get_linkedin_connections():
    # Get form inputs
    username_input = request.form.get("username")
    password = request.form.get("password")
    mfa_key = request.form.get("mfa_key")

    # Validate inputs
    if not username_input or not password or not mfa_key:
        return jsonify({"status": "error", "message": "Missing username or password or mfa key"}), 400

    try:
        # LinkedIn API query params
        params = {
            "decorationId": "com.linkedin.voyager.dash.deco.web.mynetwork.ConnectionList-16",
            "count": "100",
            "q": "search",
            "sortType": "FIRSTNAME_LASTNAME",
            "start": "0"
        }

        # Try loading cookies
        cookie_str, csrf_token, username = load_cookies(username_input)
        headers = get_headers()

        # If cookies available, use them
        if cookie_str and csrf_token:
            headers['cookie'] = cookie_str
            headers['csrf-token'] = csrf_token
        else:
            # Create cookies if not found
            cookie_create(username_input, password, mfa_key)
            cookie_str, csrf_token, username = load_cookies(username_input)
            headers['cookie'] = cookie_str
            headers['csrf-token'] = csrf_token

        # Send request to LinkedIn Voyager API
        response = requests.get(BASE_URL, headers=headers, params=params, verify=False)

        # If failed, try refreshing cookie
        if response.status_code != 200:
            cookie_create(username_input, password, mfa_key)
            cookie_str, csrf_token, username = load_cookies(username_input)
            headers['cookie'] = cookie_str
            headers['csrf-token'] = csrf_token
            # Again sending request to LinkedIn Voyager API with updated cookies
            response = requests.get(BASE_URL, headers=headers, params=params, verify=False)

        # If success, extract and return profiles
        if response.status_code == 200:
            data = response.json()
            profile_list = []
            included = data.get("included", [])
            profiles = [item for item in included if
                        item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Profile"]
            for profile_iter in profiles:
                profile_list.append({"name": profile_iter["profilePicture"]["a11yText"],
                                     "url": "https://www.linkedin.com/in/" + profile_iter["publicIdentifier"],
                                     "headline": profile_iter["headline"]
                                     })
            return jsonify({
                "status": "success",
                "message": "Connections fetched successfully.",
                "data": profile_list,
                "account_logged_in_user": username,
            }), 200
        else:
            # Return error message
            return jsonify({
                "status": "error",
                "message": f"LinkedIn API failed with status {response.status_code}"
            }), response.status_code

    except Exception as e:
        # Return error message
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
