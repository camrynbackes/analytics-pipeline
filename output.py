import csv
import os
from datetime import date
from database import get_connection
from dotenv import load_dotenv

load_dotenv()

def generate_trend_report(output_file=None):
    if output_file is None:
        output_file = f"data/trend_report_{date.today().isoformat()}.csv"

    conn = get_connection()
    cursor = conn.cursor()

    # Get the last 5 weeks of data (current week + 4 weeks for rolling average)
    cursor.execute("""
        SELECT DISTINCT week_start
        FROM gold_skill_counts
        ORDER BY week_start DESC
        LIMIT 5
    """)
    weeks = [row[0] for row in cursor.fetchall()]

    if not weeks:
        print("No data found in gold_skill_counts")
        conn.close()
        return

    current_week = weeks[0]
    print(f"Current week: {current_week}")
    print(f"Weeks available for analysis: {len(weeks)}")

    # Get current week counts — combined across sources
    cursor.execute("""
        SELECT skill, SUM(count) as total_count
        FROM gold_skill_counts
        WHERE week_start = %s
        GROUP BY skill
        ORDER BY total_count DESC
    """, (current_week,))
    current_rows = cursor.fetchall()

    # Calculate 4-week rolling average (excluding current week)
    rolling_avg = {}
    if len(weeks) > 1:
        # Use up to 4 previous weeks (not including current week)
        prev_weeks = weeks[1:5]  # Skip current week, take up to next 4

        cursor.execute("""
            SELECT skill, AVG(total_count) as avg_count
            FROM (
                SELECT skill, week_start, SUM(count) as total_count
                FROM gold_skill_counts
                WHERE week_start = ANY(%s)
                GROUP BY skill, week_start
            ) as weekly_totals
            GROUP BY skill
        """, (prev_weeks,))

        for skill, avg_count in cursor.fetchall():
            rolling_avg[skill] = round(avg_count, 1)

        print(f"Rolling average calculated from {len(prev_weeks)} previous week(s)")

    conn.close()

    # Build report rows
    report_rows = []
    for rank, (skill, count) in enumerate(current_rows, start=1):
        avg_count = rolling_avg.get(skill)

        if avg_count is None:
            change = None
            pct_change = None
            trend = "new"
        else:
            change = count - avg_count
            pct_change = round((change / avg_count) * 100, 1) if avg_count > 0 else None
            if change > 5:  # More than 5 mentions above average
                trend = "up"
            elif change < -5:  # More than 5 mentions below average
                trend = "down"
            else:
                trend = "stable"

        report_rows.append({
            "rank": rank,
            "skill": skill,
            "count": count,
            "four_week_avg": avg_count if avg_count else "n/a",
            "change_vs_avg": f"+{round(change, 1)}" if change and change > 0 else str(round(change, 1)) if change is not None else "n/a",
            "pct_change": f"{pct_change}%" if pct_change is not None else "n/a",
            "trend": trend,
            "week_start": current_week
        })

    # Write to csv
    os.makedirs("data", exist_ok=True)
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank", "skill", "count", "four_week_avg",
            "change_vs_avg", "pct_change", "trend", "week_start"
        ])
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"\nReport saved to {output_file}")
    print(f"Total skills: {len(report_rows)}")
    print(f"\nTop 10 skills this week:")
    for row in report_rows[:10]:
        avg_display = row['four_week_avg'] if row['four_week_avg'] != "n/a" else "new"
        print(f"  {row['rank']}. {row['skill']} — {row['count']} (4-wk avg: {avg_display}, {row['trend']})")

if __name__ == "__main__":
    generate_trend_report()