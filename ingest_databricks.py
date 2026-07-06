import requests
import time
from bs4 import BeautifulSoup
from datetime import date
from dotenv import load_dotenv
from database import get_connection

load_dotenv()

def scrape_databricks_sessions():
    all_sessions = []

    url = "https://www.databricks.com/dataaisummit/agenda"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    sessions = soup.find_all("a", class_="font-sans text-xl leading-7 text-orange-800 font-semibold hover:underline")

    for s in sessions:
        title = s.get_text(strip=True)
        href = s.get("href", "")
        all_sessions.append({
            "title": title,
            "url": f"https://www.databricks.com{href}",
            "source": "databricks_summit",
            "date_pulled": date.today().isoformat()
        })

    print(f"Scraped {len(all_sessions)} sessions (first page only)")
    print("Note: full pagination requires Playwright — roadmap item for v2")
    return all_sessions

def save_bronze_sessions(sessions):
    conn = get_connection()
    cursor = conn.cursor()
    new_sessions = 0
    repeat_sessions = 0

    for session in sessions:
        cursor.execute("""
            INSERT INTO bronze_conference_sessions (title, url, source, date_pulled)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (url, date_pulled) DO NOTHING
        """, (
            session["title"],
            session["url"],
            session["source"],
            session["date_pulled"]
        ))

        if cursor.rowcount == 1:
            new_sessions += 1
        else:
            repeat_sessions += 1

    conn.commit()
    conn.close()
    print(f"Bronze: {new_sessions} new sessions, {repeat_sessions} duplicates skipped")

if __name__ == "__main__":
    sessions = scrape_databricks_sessions()
    save_bronze_sessions(sessions)