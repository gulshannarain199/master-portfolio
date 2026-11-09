
"""Batch runner for configured CSV and XLSX inputs."""

from pathlib import Path
import sys
import data_quality_engine

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"

# Per-file overrides. Unlisted files default to header-based reading.
# Headerless files MUST specify has_header=False and column_order explicitly.
FILE_CONFIGS = {
    "no_header_test.csv": {
        "has_header": False,
        "column_order": ("CustomerID", "Name", "Email", "City"),
    },
    "no_header_test.xlsx": {
        "has_header": False,
        "column_order": ("CustomerID", "Name", "Email", "City"),
    },
}


def main():
    files = sorted(
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.casefold() in {".csv", ".xlsx"}
    )

    if not files:
        print(f"No supported input files found in: {INPUT_DIR}")
        return {"discovered": 0, "completed": 0, "failed": 0}

    completed = failed = 0

    for path in files:
        print(f"\n{'=' * 55}\nProcessing: {path.name}\n{'=' * 55}")

        try:
            config = FILE_CONFIGS.get(path.name, {})

            if data_quality_engine.main(path, **config):
                completed += 1
            else:
                failed += 1
                print(f"FAILED: {path.name}: Processing did not complete.")

        except Exception as exc:
            failed += 1
            print(f"FAILED: {path.name}: {exc}")

    result = {
        "discovered": len(files),
        "completed": completed,
        "failed": failed,
    }

    print("\nBATCH SUMMARY")
    print(f"Files discovered: {result['discovered']}")
    print(f"Files completed: {completed}")
    print(f"Files failed: {failed}")

    return result


if __name__ == "__main__":
    summary = main()
    sys.exit(1 if summary["failed"] > 0 else 0)
