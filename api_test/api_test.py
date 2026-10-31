import requests
from dotenv import load_dotenv
import os

load_dotenv()



tenant_id = os.getenv("BC_TENANT_ID")
client_id = os.getenv("BC_CLIENT_ID")
client_secret = os.getenv("BC_CLIENT_SECRET")
bc_env = os.getenv("BC_ENVIRONMENT")

base_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

token_data = {
    "grant_type": "client_credentials", 
    "client_id" : client_id,
    "client_secret" : client_secret, 
    "scope": "https://api.businesscentral.dynamics.com/.default"
}

# print(base_url)

#make a GET request

response = requests.post(base_url, data = token_data)
response.json()
print(response.status_code)

token = response.json()["access_token"]

print(token)