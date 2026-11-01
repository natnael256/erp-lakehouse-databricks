import requests
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from datetime import date



# Settings: secrets come from .env in the repo root
load_dotenv()
tenant_id = os.getenv("BC_TENANT_ID")
client_id = os.getenv("BC_CLIENT_ID")
client_secret = os.getenv("BC_CLIENT_SECRET")
bc_env = os.getenv("BC_ENVIRONMENT")

COMPANY_NAME = "CRONUS USA, Inc."
ENTITIES = ["customers", "items", "salesOrders", "salesInvoices"]


API_BASE = f"https://api.businesscentral.dynamics.com/v2.0/{tenant_id}/{bc_env}/api/v2.0"
REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "data" / "business_central" / date.today().isoformat()

# microsoft accss token 
def get_token():

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    form  = {
        "grant_type": "client_credentials", 
        "client_id" : client_id,
        "client_secret" : client_secret, 
        "scope": "https://api.businesscentral.dynamics.com/.default"
    }

    #make a post request
    response = requests.post(url, data = form , timeout=30)
    response.raise_for_status()

    return response.json()["access_token"]

def get_all(url, headers):
    """GET a URL and follow @odata.nextLink until every page is collected."""
    rows = []
    while url:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        body = r.json()
        rows.extend(body["value"])           # records are in "value"
        url = body.get("@odata.nextLink")    # None when there are no more pages
    return rows



def main():
    headers = {"Authorization": f"Bearer {get_token()}"}

    # find the CRONUS company id
    companies = get_all(f"{API_BASE}/companies", headers)
    company = next((c for c in companies if c["name"] == COMPANY_NAME), None)
    if company is None:
        names = [c["name"] for c in companies]
        raise SystemExit(f"Company '{COMPANY_NAME}' not found. Found: {names}")

    # pull each entity and save it as one JSON file per day
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for entity in ENTITIES:
        rows = get_all(f"{API_BASE}/companies({company['id']})/{entity}", headers)
        path = OUT_DIR / f"{entity}.json"
        path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"{entity}: {len(rows)} rows -> {path}")



if __name__ == "__main__":
    main()