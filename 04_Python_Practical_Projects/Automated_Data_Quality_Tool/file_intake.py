"""Interactive input-file selector for CSV and XLSX files."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"

def get_input_file():
    files = sorted(p for p in INPUT_DIR.iterdir()
                   if p.is_file() and p.suffix.casefold() in {".csv", ".xlsx"})
    if not files:
        raise FileNotFoundError(f"No CSV or XLSX files found in: {INPUT_DIR}")
    print("\nAvailable input files:")
    for n, path in enumerate(files, 1):
        print(f"{n}. {path.name}")
    while True:
        try:
            choice = int(input("\nEnter the number of the file to process: "))
            if 1 <= choice <= len(files):
                selected = files[choice - 1]
                print(f"\nSelected: {selected.name}")
                print(f"Full path: {selected}")
                print(f"File size: {selected.stat().st_size} bytes")
                return selected
        except ValueError:
            pass
        print("Invalid choice. Please enter a listed number.")

if __name__ == "__main__":
    get_input_file()
