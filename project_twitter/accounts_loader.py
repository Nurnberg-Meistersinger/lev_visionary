import json
import os
import re
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


def create_custom_set(set_name: str, handles: list[str]) -> dict:
    """Создаёт новый кастомный JSON-файл набора аккаунтов."""
    if not re.match(r'^[a-z0-9_]+$', set_name):
        raise ValueError("Название должно содержать только строчную латиницу, цифры и _")
    file_path = SETS_DIR / f"{set_name}.json"
    if file_path.exists():
        raise ValueError(f"Сет '{set_name}' уже существует")
    accounts = [
        {"handle": h.lstrip("@"), "name": h.lstrip("@")}
        for h in handles if h.strip()
    ]
    if not accounts:
        raise ValueError("Нужно указать хотя бы один аккаунт")
    data = {
        "name": set_name.replace("_", " ").title(),
        "description": "Кастомный сет",
        "custom": True,
        "accounts": accounts,
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def add_to_custom_set(set_name: str, handles: list[str]) -> tuple[dict, list[dict]]:
    """Добавляет аккаунты в существующий кастомный сет."""
    file_path = SETS_DIR / f"{set_name}.json"
    if not file_path.exists():
        raise ValueError(f"Сет '{set_name}' не найден")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("custom"):
        raise ValueError(f"'{set_name}' — встроенный сет, редактировать нельзя")
    existing_handles = {acc["handle"].lower() for acc in data["accounts"]}
    new_accounts = [
        {"handle": h.lstrip("@"), "name": h.lstrip("@")}
        for h in handles
        if h.strip() and h.lstrip("@").lower() not in existing_handles
    ]
    if not new_accounts:
        raise ValueError("Все указанные аккаунты уже есть в сете")
    data["accounts"].extend(new_accounts)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data, new_accounts


def delete_custom_set(set_name: str) -> None:
    """Удаляет кастомный сет."""
    file_path = SETS_DIR / f"{set_name}.json"
    if not file_path.exists():
        raise ValueError(f"Сет '{set_name}' не найден")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("custom"):
        raise ValueError(f"'{set_name}' — встроенный сет, удалять нельзя")
    file_path.unlink()


def is_custom_set(set_name: str) -> bool:
    """Возвращает True, если сет кастомный (создан через бот)."""
    file_path = SETS_DIR / f"{set_name}.json"
    if not file_path.exists():
        return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("custom"))
    except Exception:
        return False
