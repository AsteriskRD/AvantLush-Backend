import requests

headers = {
    "Authorization": "Bearer 7f340fd7-6aff-16c8-4740-a3cc8b811a6b",
    "Accept": "application/json"
}

url = "https://apisandbox.dev.clover.com/v3/merchants/X4SS3ZCHCN4S1"

print(f"Testing URL: {url}")
print(f"Headers: {headers}")

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")