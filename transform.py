from datetime import date
from database import get_connection
from skills import extract_skills

def build_silver(date_pulled=None):
    if date_pulled is None:
        date_pulled = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.id, b.title, b.company, b.description, b.source
        FROM bronze_jobs b
        JOIN bronze_job_snapshots s ON b.id = s.job_id
        WHERE s.date_pulled = %s
        AND NOT EXISTS (
            SELECT 1 FROM silver_skills ss WHERE ss.job_id = b.id
        )
    """, (date_pulled,))

    jobs = cursor.fetchall()
    print(f"Processing {len(jobs)} jobs from bronze")

    silver_rows = []
    for job_id, title, company, description, source in jobs:
        skills = extract_skills(description or "")
        for skill in skills:
            silver_rows.append((job_id, title, company, skill, source, date_pulled))

    if silver_rows:
        cursor.executemany("""
            INSERT INTO silver_skills (job_id, title, company, skill, source, date_pulled)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, silver_rows)

    conn.commit()
    conn.close()
    print(f"Silver jobs: {len(silver_rows)} skill rows saved")


def build_silver_conferences(date_pulled=None):
    if date_pulled is None:
        date_pulled = date.today().isoformat()

    print(f"Looking for conference sessions on: {date_pulled}")

    conn = get_connection()
    cursor = conn.cursor()

    # debug: check what's in bronze_conference_sessions
    cursor.execute("SELECT COUNT(*) FROM bronze_conference_sessions WHERE date_pulled = %s", (date_pulled,))
    count = cursor.fetchone()[0]
    print(f"Sessions in bronze for {date_pulled}: {count}")

    # debug: check what's in silver_skills for databricks
    cursor.execute("SELECT COUNT(*) FROM silver_skills WHERE source = 'databricks_summit'")
    silver_count = cursor.fetchone()[0]
    print(f"Existing databricks rows in silver: {silver_count}")

    cursor.execute("""
        SELECT id, title, source
        FROM bronze_conference_sessions
        WHERE date_pulled = %s
        AND CAST(id AS TEXT) NOT IN (
            SELECT DISTINCT job_id FROM silver_skills
            WHERE source = 'databricks_summit'
        )
    """, (date_pulled,))

    sessions = cursor.fetchall()
    print(f"Processing {len(sessions)} conference sessions")
    
    # debug: print first 3 session titles to confirm extraction
    for session_id, title, source in sessions[:3]:
        skills = extract_skills(title or "")
        print(f"  Title: {title[:50]}")
        print(f"  Skills found: {skills}")

    silver_rows = []
    for session_id, title, source in sessions:
        skills = extract_skills(title or "")
        for skill in skills:
            silver_rows.append((str(session_id), title, "n/a", skill, source, date_pulled))

    if silver_rows:
        cursor.executemany("""
            INSERT INTO silver_skills (job_id, title, company, skill, source, date_pulled)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, silver_rows)

    conn.commit()
    conn.close()
    print(f"Silver conferences: {len(silver_rows)} skill rows saved")


def build_gold(date_pulled=None):
    if date_pulled is None:
        date_pulled = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill, source, COUNT(*) as count
        FROM silver_skills
        WHERE date_pulled = %s
        GROUP BY skill, source
        ORDER BY count DESC
    """, (date_pulled,))

    rows = cursor.fetchall()
    print(f"Building gold from {len(rows)} skill/source combinations")

    if rows:
        cursor.executemany("""
            INSERT INTO gold_skill_counts (skill, source, count, week_start)
            VALUES (%s, %s, %s, %s)
        """, [(skill, source, count, date_pulled) for skill, source, count in rows])

    conn.commit()
    conn.close()
    print(f"Gold: {len(rows)} skill counts saved for {date_pulled}")


if __name__ == "__main__":
    build_silver()
    build_silver_conferences()
    build_gold()