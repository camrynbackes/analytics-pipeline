import csv
import os
from datetime import date, timedelta
from database import get_connection
from dotenv import load_dotenv

load_dotenv()

def generate_trend_report(output_file=None):
    if output_file is None:
        output_file = f"data/trend_report_{date.today().isoformat()}.csv"

    conn = get_connection()
    cursor = conn.cursor()

    # get the two most recent week_start dates
    cursor.execute("""
        SELECT DISTINCT week_start 
        FROM gold_skill_counts 
        ORDER BY week_start DESC 
        LIMIT 2
    """)
    weeks = [row[0] for row in cursor.fetchall()]

    if not weeks:
        print("No data found in gold_skill_counts")
        return

    current_week = weeks[0]
    prev_week = weeks[1] if len(weeks) > 1 else None

    print(f"Current week: {current_week}")
    print(f"Previous week: {prev_week if prev_week else 'no previous data yet'}")

    # get current week counts
    cursor.execute("""
        SELECT skill, source, count
        FROM gold_skill_counts
        WHERE week_start = %s
        ORDER BY count DESC
    """, (current_week,))
    current_rows = cursor.fetchall()

    # get previous week counts into a lookup dict
    prev_counts = {}
    if prev_week:
        cursor.execute("""
            SELECT skill, source, count
            FROM gold_skill_counts
            WHERE week_start = %s
        """, (prev_week,))
        for skill, source, count in cursor.fetchall():
            prev_counts[(skill, source)] = count

    conn.close()

    # build report rows
    report_rows = []
    for rank, (skill, source, count) in enumerate(current_rows, start=1):
        prev_count = prev_counts.get((skill, source))

        if prev_count is None:
            change = None
            pct_change = None
            trend = "new"
        else:
            change = count - prev_count
            pct_change = round((change / prev_count) * 100, 1) if prev_count > 0 else None
            if change > 0:
                trend = "up"
            elif change < 0:
                trend = "down"
            else:
                trend = "flat"

        report_rows.append({
            "rank": rank,
            "skill": skill,
            "source": source,
            "count": count,
            "prev_count": prev_count if prev_count else "n/a",
            "change": f"+{change}" if change and change > 0 else str(change) if change is not None else "n/a",
            "pct_change": f"{pct_change}%" if pct_change is not None else "n/a",
            "trend": trend,
            "week_start": current_week
        })

    # write to csv
    os.makedirs("data", exist_ok=True)
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank", "skill", "source", "count", "prev_count",
            "change", "pct_change", "trend", "week_start"
        ])
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"\nReport saved to {output_file}")
    print(f"Total skills: {len(report_rows)}")
    print(f"\nTop 10 skills this week:")
    for row in report_rows[:10]:
        print(f"  {row['rank']}. {row['skill']} — {row['count']} ({row['trend']})")

if __name__ == "__main__":
    generate_trend_report()