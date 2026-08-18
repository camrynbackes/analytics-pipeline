import requests
import json
import re
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

    # Extract embedded JSON data from the Next.js page
    # The page embeds all session data in a <script id="__NEXT_DATA__"> tag
    try:
        # Find the JSON data embedded in the page
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', response.text, re.DOTALL)
        if not match:
            print("Could not find embedded session data")
            return []

        data = json.loads(match.group(1))
        sessions_data = data.get('props', {}).get('pageProps', {}).get('agenda', {}).get('sessions', [])

        if not sessions_data:
            print("No sessions found in embedded data")
            return []

        # Extract session information from the JSON
        for session in sessions_data:
            title = session.get('title', '')
            alias = session.get('alias', '')

            all_sessions.append({
                "title": title,
                "url": f"https://www.databricks.com{alias}" if alias else "",
                "source": "databricks_summit",
                "date_pulled": date.today().isoformat()
            })

        print(f"Scraped {len(all_sessions)} sessions from embedded data")
        total_sessions = len(sessions_data)
        print(f"Total sessions available: {total_sessions}")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing session data: {e}")
        return []

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