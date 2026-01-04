import json
import os
from pathlib import Path

SETS_DIR = Path(__file__).resolve().parent / "account_sets"


def _load_set(set_name: str) -> list[dict]:
    file_path = SETS_DIR / f"{set_name}.json"
    if not file_path.exists():
        raise FileNotFoundError(
            f"Account set '{set_name}' not found in {SETS_DIR}"
        )
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["accounts"]


def list_available_sets() -> list[str]:
    return sorted(p.stem for p in SETS_DIR.glob("*.json"))


def _normalize_set_names(selected_sets: str | None) -> list[str]:
    if not selected_sets:
        selected_sets = os.getenv("PROJECT_TWITTER_ACCOUNT_SETS", "all")

    set_names = [s.strip() for s in selected_sets.split(",") if s.strip()]
    if not set_names:
        set_names = ["all"]

    return set_names


def load_accounts(selected_sets: str | None = None) -> list[dict]:
    set_names = _normalize_set_names(selected_sets)

    accounts = []
    seen = set()
    for set_name in set_names:
        for account in _load_set(set_name):
            key = account["handle"].lower()
            if key in seen:
                continue
            seen.add(key)
            accounts.append(account)

    return accounts


def selected_sets(selected_sets: str | None = None) -> list[str]:
    return _normalize_set_names(selected_sets)
