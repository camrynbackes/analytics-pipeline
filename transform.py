import json
import csv
from datetime import date
from collections import Counter


#Silver layer
import os
print(os.listdir())

with open("bronze_jobs_2026-06-10.json", "r") as f:
    all_jobs = json.load(f)

from skills import SKILLS, extract_skills

silver_rows = []
for job in all_jobs:
    skills = extract_skills(job["description"])
    for skill in skills:
        silver_rows.append({
            "job_id": job["id"],
            "title": job["title"],
            "company": job["company"]["display_name"],
            "skill": skill,
            "source": "adzuna",
            "date_pulled": date.today().isoformat()
        })

filename = f"data/silver_skills_{date.today().isoformat()}.csv"

with open(filename, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["job_id", "title", "company", "skill", "source", "date_pulled"])
    writer.writeheader()
    writer.writerows(silver_rows)

print(f"Silver: {len(silver_rows)} skill rows saved")


# Gold layer
with open("data/silver_skills_2026-06-10.csv", "r") as f:
    reader = csv.DictReader(f)
    all_skills = [row["skill"] for row in reader]

skill_counts = Counter(all_skills)

with open("gold_skill_counts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["skill", "count"])
    for skill, count in skill_counts.most_common():
        writer.writerow([skill, count])

print(f"Gold: {len(skill_counts)} skills ranked")