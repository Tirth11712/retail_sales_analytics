"""One-click runner: generates the dataset, then runs the full analysis."""
import subprocess
import sys

for script in ("generate_dataset.py", "retail_analysis.py"):
    print(f">>> Running {script}")
    if subprocess.call([sys.executable, script]) != 0:
        sys.exit(f"{script} failed")
