import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parent
raise SystemExit(subprocess.run(
    [sys.executable, "multi_file_consolidation.py"], cwd=project
).returncode)
