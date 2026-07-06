import subprocess
import sys

sys.stdout.flush()
print("Starting weekly pipeline run...", flush=True)

scripts = [
    ("Ingest Adzuna", "ingest_adzuna.py"),
    ("Ingest Databricks", "ingest_databricks.py"),
    ("Transform", "transform.py"),
    ("Output", "output.py"),
]

for name, script in scripts:
    print(f"\n--- {name} ---")
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: {script} failed with return code {result.returncode}")
        sys.exit(1)
    print(f"{name} completed successfully")

print("\nPipeline complete.")