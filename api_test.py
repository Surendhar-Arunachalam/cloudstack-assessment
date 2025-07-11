import requests

url = "http://127.0.0.1:5000/linkedin/connections"

payload = {
    'username': 'test@gmail.com',
    'password': 'test1234',
    'session_persistence': 'True'  # True|False
}

response = requests.request("POST", url, data=payload)

print(response.text)
