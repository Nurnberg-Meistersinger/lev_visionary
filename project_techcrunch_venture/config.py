import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env из корневой директории проекта
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

TECHCRUNCH_URL = "https://techcrunch.com/category/venture/"

MAX_ITEMS = 3
