import os
import json
from typing import Any, Dict
from datetime import datetime
from config.ibkr_settings import DATA_DIR

os.makedirs(DATA_DIR, exist_ok=True)


def save_json(rel_path: str, payload: Dict[str, Any]) -> None:
    full_path = os.path.join(DATA_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def append_log(rel_path: str, line: str) -> None:
    full_path = os.path.join(DATA_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z {line}\n")


def load_json(rel_path: str, default: Any = None) -> Any:
    full_path = os.path.join(DATA_DIR, rel_path)
    if not os.path.exists(full_path):
        return default
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

