"""Generate and run synthetic Client Case Study 02."""
from pathlib import Path
import subprocess
import sys

import multi_file_consolidation as consolidation

project = Path(__file__).resolve().parent
package = project / "Client_Case_02_Package"
generator = package / "generate_case_02_excel.py"
config = package / "client_case_02_sources.json"
output = project / "output" / "client_case_02"

subprocess.run([sys.executable, str(generator)], check=True)
result = consolidation.run_consolidation(
    package_dir=package,
    output_dir=output,
    config_path=config,
    output_prefix="client_case_02",
)
for key, value in result.items():
    print(f"{key}: {value}")
