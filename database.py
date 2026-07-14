import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    import psycopg2
    supabase_url = os.getenv("SUPABASE_CONNECTION_STRING")
    return psycopg2.connect(supabase_url)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze_conference_sessions (
            id SERIAL PRIMARY KEY,
            title TEXT,
            url TEXT,
            source TEXT,
            date_pulled DATE,
            UNIQUE (url, date_pulled)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze_jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            date_posted TEXT,
            source TEXT,
            date_first_seen DATE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bronze_job_snapshots (
            job_id TEXT,
            date_pulled DATE,
            PRIMARY KEY (job_id, date_pulled)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS silver_skills (
            id SERIAL PRIMARY KEY,
            job_id TEXT,
            title TEXT,
            company TEXT,
            skill TEXT,
            source TEXT,
            date_pulled DATE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_skill_counts (
            id SERIAL PRIMARY KEY,
            skill TEXT,
            count INTEGER,
            source TEXT,
            week_start DATE
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized")

if __name__ == "__main__":
    initialize_db()