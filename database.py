import sqlite3
import os

DB_PATH = "data/pipeline.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_db():
    os.makedirs("data", exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""

        CREATE TABLE IF NOT EXISTS bronze_jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            date_posted TEXT,
            source TEXT,
            date_first_seen DATE
        );

        CREATE TABLE IF NOT EXISTS bronze_job_snapshots (   
            job_id TEXT,
            date_pulled DATE,
            PRIMARY KEY (job_id, date_pulled)
        );

        CREATE TABLE IF NOT EXISTS silver_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            title TEXT,
            company TEXT,
            skill TEXT,
            source TEXT,
            date_pulled DATE
        );

        CREATE TABLE IF NOT EXISTS gold_skill_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT,
            count INTEGER,
            source TEXT,
            week_start DATE
        );

    """)

    conn.commit()
    conn.close()
    print("Database initialized") 

if __name__ == "__main__":
    initialize_db()
 