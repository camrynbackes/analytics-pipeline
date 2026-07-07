# Data Analytics Trends Pipeline

A production-style data pipeline that ingests job postings and conference session data weekly, extracts skill and tool mentions, and surfaces trending technologies in the data analytics field. Built as a solo end-to-end engineering project over 4 weeks.

---

## Overview

The data analytics field evolves quickly — tools rise and fall, new frameworks emerge, and employer expectations shift. This pipeline answers the question: **what skills and technologies are trending in data analytics right now, and are they growing or declining week over week?**

It pulls from two complementary sources:
- **Adzuna API** — thousands of live job postings across data analytics roles, representing employer demand
- **Databricks Data + AI Summit agenda** — conference session titles representing practitioner focus and emerging topics

These sources are intentionally chosen to triangulate signal: job postings reflect what organizations need today, conference talks reflect where the field is heading.

---

## Architecture

The pipeline follows a **bronze / silver / gold** medallion architecture — a standard pattern in production data engineering for separating raw ingestion from transformation and aggregation.

```
Sources          Bronze              Silver                Gold
─────────        ──────────────      ──────────────────    ──────────────────
Adzuna API   →   bronze_jobs         silver_skills         gold_skill_counts
                 bronze_job_         (one row per          (aggregated skill
                 snapshots           job × skill)          counts per week)
Databricks   →   bronze_conference_
Summit           sessions
```

**Bronze** — raw data preserved exactly as received from each source. Job descriptions are stored once and never overwritten; a separate snapshots table tracks which weeks each job was active. This immutability means transformation logic can be rerun against historical data without re-hitting APIs.

**Silver** — structured extraction layer. Skill and tool mentions are identified from raw text using regex-based keyword matching with word boundary enforcement (preventing false positives like "wait" matching "ai"). Each row represents a single skill mention in a single job or session.

**Gold** — weekly aggregated counts per skill per source, with a `week_start` timestamp. This enables trend queries across weeks using SQL window functions.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, Requests, BeautifulSoup |
| Storage | Supabase (hosted Postgres) |
| Transformation | Python, psycopg2, regex |
| Orchestration | GitHub Actions (weekly pull) |
| Output | CSV trend report, Supabase Table Editor |

---

## Data Sources

### Adzuna API (Job Postings)
- **Access**: Free tier, 2,500 requests/month
- **Volume**: ~1,000–2,000 unique job postings per weekly run
- **Search terms**: `data analyst`, `business intelligence analyst`, `analytics engineer`, `marketing analyst`, `product analyst`
- **Rate limit design**: Pipeline uses ~100 requests per run (5 terms × 10 pages × 2 requests buffer), leaving headroom for debugging and future sources
- **Deduplication**: Jobs are stored once in `bronze_jobs` using `INSERT ... ON CONFLICT DO NOTHING`. A separate `bronze_job_snapshots` table tracks weekly activity without re-storing descriptions — separating content from activity

### Databricks Data + AI Summit
- **Access**: Public agenda, scraped via BeautifulSoup
- **Volume**: 18 sessions (first page) — full pagination requires Playwright (v2 roadmap)
- **Note**: Session titles are shorter than job descriptions and surface different signal — architecture patterns and emerging tools rather than explicit skill requirements

---

## Skill Extraction

Skills are matched against a predefined taxonomy of ~150 terms across categories: programming languages, libraries, databases, cloud platforms, BI tools, ML/AI frameworks, and analytics concepts.

Each term supports multiple aliases — for example, `snowflake` matches both `"snowflake"` and `"snowflake data warehouse"`. Matching uses Python `re` with `\b` word boundaries to prevent substring false positives.

```python
def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill, aliases in SKILLS.items():
        for alias in aliases:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill)
                break
    return found
```

This approach was chosen over general NLP (KeyBERT, RAKE) because the goal is measuring demand for *known* tools, not discovering unknown topics. Predefined taxonomy gives full control over what's counted and makes results immediately interpretable.

---

## Database Schema

```sql
-- raw job postings, stored once per unique job
bronze_jobs (id PK, title, company, location, description, date_posted, source, date_first_seen)

-- tracks which weeks each job was active (append-only)
bronze_job_snapshots (job_id, date_pulled, PRIMARY KEY (job_id, date_pulled))

-- raw conference session titles
bronze_conference_sessions (id SERIAL PK, title, url, source, date_pulled, UNIQUE (url, date_pulled))

-- one row per job/session × skill (append-only)
silver_skills (id SERIAL PK, job_id, title, company, skill, source, date_pulled)

-- aggregated weekly skill counts
gold_skill_counts (id SERIAL PK, skill, source, count, week_start, UNIQUE (skill, source, week_start))
```

---

## Weekly Output

Each run generates a CSV trend report saved to `data/` and committed to this repo:

```
rank | skill  | count | prev_count | change | pct_change | trend | week_start
1    | sql    | 450   | 420        | +30    | +7.1%      | up    | 2026-07-07
2    | python | 380   | 410        | -30    | -7.3%      | down  | 2026-07-07
3    | dbt    | 120   | n/a        | n/a    | n/a        | new   | 2026-07-07
```

`trend` values: `up`, `down`, `flat`, `new` (first appearance).

---

## Automation

The pipeline runs every Monday at 9am UTC via GitHub Actions with zero manual intervention required. Credentials are stored as GitHub repository secrets and injected at runtime — never hardcoded.

```
GitHub Actions → pulls latest code → installs dependencies
→ hits Adzuna API → scrapes Databricks agenda
→ writes bronze → extracts silver → aggregates gold (all in Supabase)
→ generates trend CSV → commits report back to repo
```

---

## Running Locally

```bash
# clone and set up environment
git clone https://github.com/camrynbackes/analytics-pipeline
cd analytics-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# configure credentials
cp .env.example .env
# add ADZUNA_APP_ID, ADZUNA_APP_KEY, SUPABASE_CONNECTION_STRING

# initialize database
python database.py

# run full pipeline
python run_pipeline.py
```

---

## Project Structure

```
analytics-pipeline/
├── .github/workflows/weekly_pipeline.yml  # GitHub Actions schedule
├── ingest_adzuna.py                        # Adzuna API ingestion
├── ingest_databricks.py                   # Databricks agenda scraper
├── transform.py                           # Silver and gold layer transforms
├── output.py                              # Weekly trend CSV generation
├── skills.py                              # Skill taxonomy and extraction logic
├── database.py                            # Supabase connection and schema
├── run_pipeline.py                        # Pipeline orchestrator
├── requirements.txt
└── data/
    └── trend_report_YYYY-MM-DD.csv        # Weekly reports (auto-committed)
```

---

## Known Limitations

- **Databricks scraper**: Captures first page only (18 sessions) due to JavaScript-rendered pagination. Full scraping via Playwright is planned for v2.
- **Adzuna free tier**: 2,500 requests/month limits weekly volume. A paid tier or additional job board APIs would improve sample size.
- **Sampling bias**: Remote-friendly job boards and practitioner conferences over-represent modern stack tools (dbt, Snowflake, Airflow) relative to the broader market. Mid-market tooling is likely under-counted.
- **Keyword matching**: Predefined taxonomy requires manual updates to capture newly emerging tools. Does not handle contextual negation ("no experience with Tableau required").

---

## Roadmap

- [ ] Add Playwright-based full pagination for Databricks (805 sessions)
- [ ] Add Reddit API source (`r/dataengineering`, `r/dataanalytics`)
- [ ] Add second job board source to increase volume and reduce Adzuna dependency
- [ ] Build dashboard for interactive trend visualization
- [ ] Add dbt for transform layer with data quality tests
- [ ] Implement seniority-level filtering to segment trends by role level

---

## Design Decisions

A few deliberate choices worth noting:

**Append-only bronze layer** — raw data is never updated or deleted. This means transformation logic can be rerun against any historical week without re-hitting APIs, and any bug in extraction can be fixed retroactively.

**Separate content from activity** — `bronze_jobs` stores job descriptions once; `bronze_job_snapshots` records which weeks each job appeared. This prevents storing duplicate descriptions for jobs that stay open across multiple weeks while preserving the activity signal.

**Predefined taxonomy over NLP** — keyword matching was chosen over KeyBERT or spaCy because the goal is measuring known tools, not discovering unknown topics. The tradeoff is manual taxonomy maintenance; the benefit is fully interpretable, auditable results.

**Rate limit budgeting** — the pipeline is explicitly designed around Adzuna's 2,500 requests/month free tier, using ~400/month (100/run × 4 runs) and leaving 2,100 as buffer. This is documented as an operational constraint, not an afterthought.
