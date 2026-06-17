import requests
import time
import os
from datetime import date
from dotenv import load_dotenv
from database import get_connection, initialize_db

result = load_dotenv()
print(f"dotenv loaded: {result}")  
print(f"current directory: {os.getcwd()}")

from dotenv import dotenv_values

config = dotenv_values()
print(config)

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

SEARCH_TERMS = [
    "data analyst",
    "business intelligence analyst", 
    "analytics engineer",
    "marketing analyst",
    "product analyst"
]

def fetch_jobs(pages=10):
    all_jobs = []

    for term in SEARCH_TERMS:
        print(f"\nFetching: {term}")
        for page in range(1, pages + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/{page}"
            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "what": term,
                "results_per_page": 50
            }

            response = requests.get(url, params=params)

            if response.status_code != 200:
                print(f"Error {response.status_code} on page {page}, skipping.")
                break

            data = response.json()

            if not data["results"]:
                print(f"No results at page {page}, stopping.")
                break

            all_jobs.extend(data["results"])
            print(f"Page {page}: {len(data['results'])} jobs fetched")
            time.sleep(1)
        
        time.sleep(2)

    return all_jobs

def save_bronze(jobs):
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    new_jobs = 0
    repeat_jobs = 0

    for job in jobs:
        cursor.execute("""
            INSERT OR IGNORE INTO bronze_jobs
            (id, title, company, location, description, date_posted, source, date_first_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["id"],
            job["title"],
            job["company"].get("display_name", "Unknown"),
            job["location"].get("display_name", "Unknown"),
            job.get("description", ""),
            job.get("created", ""),
            "adzuna",
            today
        ))

        if cursor.rowcount == 1:
            new_jobs += 1
        else:
            repeat_jobs += 1

        cursor.execute("""
            INSERT OR IGNORE INTO bronze_job_snapshots (job_id, date_pulled)
            VALUES (?, ?)
        """, (job["id"], today))

    conn.commit()
    conn.close()
    print(f"\nBronze: {new_jobs} new jobs, {repeat_jobs} duplicates skipped")

if __name__ == "__main__":
    initialize_db()
    jobs = fetch_jobs(pages=10)
    save_bronze(jobs)
    print(f"Done — {len(jobs)} total records fetched")