from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM bronze_jobs")
print(f"Bronze jobs: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM bronze_job_snapshots")
print(f"Snapshots: {cursor.fetchone()[0]}")

conn.close()