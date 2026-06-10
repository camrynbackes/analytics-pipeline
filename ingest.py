import requests
import time
from dotenv import load_dotenv
import os
import json

print(os.getcwd())

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

all_jobs = []

for page in range(1, 6):
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": "data analyst",
        "results_per_page": 50
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not data["results"]:
        print(f"No more results at page {page}, stopping.")
        break

    all_jobs.extend(data["results"])
    print(f"Page {page}: {len(data['results'])} jobs fetched")
    time.sleep(1)

print(f"Total jobs fetched: {len(all_jobs)}")

os.makedirs("data", exist_ok=True)

from datetime import date

filename = f"data/bronze_jobs_{date.today().isoformat()}.json"

with open(filename, "w") as f:
    json.dump(all_jobs, f, indent=2)

print(f"Bronze: {len(all_jobs)} raw jobs saved to {filename}")