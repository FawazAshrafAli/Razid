import requests
import hashlib

url = "https://dashboard.easebuzz.in/submerchant/v1/generate_kyc_access_key"
headers = {
    "Content-Type": "application/json"
}

merchant_key = "10PBP71ABZ2"
salt = "ABC55E8IBW"

# Create the hash string
hash_string = f"{merchant_key}|{salt}"
hash_value = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

payload = {
    "merchant_key": merchant_key,
    "salt": salt,
    "hash": hash_value
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    if data["status"] == 1:
        access_key = data["data"]["access_key"]
        print("Access Key:", access_key)
    else:
        print("Error:", data["message"])
else:
    print("HTTP Error:", response.status_code, response.text)
