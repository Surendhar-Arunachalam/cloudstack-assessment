import json
import requests
import urllib3
from flask import Flask, request, jsonify
from linkedin_login import cookie_create

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
BASE_URL = "https://www.linkedin.com/voyager/api/relationships/dash/connections"


# Load existing cookies from local file
cookie_file = 'cookies.json'
def load_cookies(cookie_file):
    try:
        with open(cookie_file, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        cookie_str = '; '.join(f'{c["name"]}={c["value"]}' for c in cookies)
        csrf_token = next((c["value"].strip('"') for c in cookies if c["name"] == "JSESSIONID"), "")
        profile_name_cookie = next((c["value"].strip('"') for c in cookies if c["name"] == "profile"), "")
    except:
        cookie_str = csrf_token = profile_name_cookie = None
    return cookie_str, csrf_token, profile_name_cookie


# Header parameters for requests
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


@app.route("/linkedin/connections", methods=["POST"])
def get_linkedin_connections():
    # Get username and password from form
    username = request.form.get("username")
    password = request.form.get("password")
    session_persistence = request.form.get("session_persistence")

    # Return error message if username or password is empty
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    try:
        # Step 1: Login and save cookies
        if session_persistence == 'False':
            cookie_create(username, password)

        # Step 2: Load cookies and make request
        cookie_str, csrf_token, login_profile_name = load_cookies(cookie_file)
        headers = get_headers()
        if cookie_str is not None and csrf_token is not None:
            headers['cookie'] = cookie_str
            headers['csrf-token'] = csrf_token
        # else:
        #     cookie_create(username, password)
        params = {
            "decorationId": "com.linkedin.voyager.dash.deco.web.mynetwork.ConnectionList-16",
            "count": "100",
            "q": "search",
            "sortType": "FIRSTNAME_LASTNAME",
            "start": "0"
        }

        # Step 3: Requests for connections URL to retrieve results with existing cookies
        response = requests.get(BASE_URL, headers=headers, params=params, verify=False)
        if response.status_code != 200:
            login_profile_name = cookie_create(username, password)
            cookies = json.loads(open('cookies.json', 'r', encoding='utf-8').read())
            cookie_str = ''
            for cookie_iter in cookies:
                if cookie_iter["name"] == "JSESSIONID":
                    csrf_token = cookie_iter["value"].strip('"')
                cookie_str += cookie_iter["name"].strip() + "=" + cookie_iter["value"].strip() + '; '
            headers['cookie'] = cookie_str
            headers['csrf-token'] = csrf_token

        # Step 4: Requests for connections URL to retrieve results with new cookies
        response = requests.get(BASE_URL, headers=headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            included = data.get("included", [])
            profiles = [item for item in included if item.get("$type") == "com.linkedin.voyager.dash.identity.profile.Profile"]

            profile_list = []
            profile_list.append({'logged_in_user': login_profile_name})
            for profile_iter in profiles:
                profile_list.append({"name": profile_iter["profilePicture"]["a11yText"],
                                     "url": "https://www.linkedin.com/in/" + profile_iter["publicIdentifier"],
                                     "headline": profile_iter["headline"]
                                     })
            return jsonify({
                "status": "success",
                "message": "Connections fetched successfully.",
                "data": profile_list
            }), 200
        # Return error message
        else:
            return jsonify({
                "status": "error",
                "message": f"LinkedIn API failed with status {response.status_code}"
            }), response.status_code

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
