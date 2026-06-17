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
        WHERE s.date_pulled = ?
        AND b.id NOT IN (
            SELECT DISTINCT job_id FROM silver_skills
        )
    """, (date_pulled,))

    jobs = cursor.fetchall()
    print(f"Processing {len(jobs)} jobs from bronze")

    silver_rows = []
    for job_id, title, company, description, source in jobs:
        skills = extract_skills(description or "")
        for skill in skills:
            silver_rows.append((job_id, title, company, skill, source, date_pulled))

    cursor.executemany("""
        INSERT INTO silver_skills (job_id, title, company, skill, source, date_pulled)
        VALUES (?, ?, ?, ?, ?, ?)
    """, silver_rows)

    conn.commit()
    conn.close()
    print(f"Silver: {len(silver_rows)} skill rows saved")

def build_gold(date_pulled=None):
    if date_pulled is None:
        date_pulled = date.today().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill, source, COUNT(*) as count
        FROM silver_skills
        WHERE date_pulled = ?
        GROUP BY skill, source
        ORDER BY count DESC
    """, (date_pulled,))

    rows = cursor.fetchall()

    cursor.executemany("""
        INSERT INTO gold_skill_counts (skill, source, count, week_start)
        VALUES (?, ?, ?, ?)
    """, [(skill, source, count, date_pulled) for skill, source, count in rows])

    conn.commit()
    conn.close()
    print(f"Gold: {len(rows)} skill counts saved for {date_pulled}")

if __name__ == "__main__":
    build_silver()
    build_gold()