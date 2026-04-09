import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json_data(filename: str):
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_data(filename: str, data):
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_latest_plan_file():
    """Finds the most recently created plan_*.json file."""
    plan_files = list(DATA_DIR.glob("plan_*.json"))
    if not plan_files:
        return None
    # Sort by creation time (most recent first)
    latest_file = max(plan_files, key=os.path.getctime)
    return latest_file.name

