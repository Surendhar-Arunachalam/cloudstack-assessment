import requests

url = "http://127.0.0.1:5000/linkedin/connections"

payload = {
    'username': 'test@gmail.com',
    'password': 'test1234',
    'mfa_key': 'ZZC6C6W563QK2FSH64FAHBURHTKX27CD'
}

response = requests.request("POST", url, data=payload)

print(response.text)
