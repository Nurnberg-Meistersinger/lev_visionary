#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Автоматическое использование виртуального окружения
VENV_DIR = Path(__file__).resolve().parent / ".the_vis"
VENV_PYTHON = VENV_DIR / "bin" / "python3"

def ensure_venv():
    """Перезапускает скрипт через Python из виртуального окружения, если необходимо"""
    # Проверяем, запущен ли скрипт из venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    # Если не в venv и venv существует - перезапускаем
    if not in_venv and VENV_PYTHON.exists():
        print(f"🔄 Перезапуск через виртуальное окружение: {VENV_PYTHON}")
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
    elif not in_venv and not VENV_PYTHON.exists():
        print(f"⚠️  Виртуальное окружение не найдено: {VENV_DIR}")
        print(f"Создайте его командой: python3 -m venv .the_vis && .the_vis/bin/pip install -r requirements.txt")

ACCOUNT_SETS_DIR = Path(__file__).resolve().parent / "project_twitter" / "account_sets"
SET_FLAGS = {
    "palantir": "palantir",
    "cypherpunk": "cypherpunk",
    "blockchain": "blockchain",
    "venture": "venture",
    "lifestyle": "lifestyle",
    "entrepreneurs": "entrepreneurs",
    "protectorium": "protectorium",
    "hackers": "hackers",
}
PROJECT_MAP = {
    "twitter": "project_twitter",
    "a16z": "project_a16z",
    "techcrunch_venture": "project_techcrunch_venture",
    "techcrunch_startup": "project_techcrunch_startup",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Утилита для запуска пайплайнов visionary"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="запустить проект")
    exclusive = run_parser.add_mutually_exclusive_group(required=False)
    exclusive.add_argument(
        "--twitter",
        action="store_true",
        help="запустить project_twitter (требуется один из наборов-флагов)",
    )
    exclusive.add_argument(
        "--a16z",
        action="store_true",
        help="запустить project_a16z",
    )
    exclusive.add_argument(
        "--techcrunch_startup",
        action="store_true",
        help="запустить project_techcrunch_startup",
    )
    exclusive.add_argument(
        "--techcrunch_venture",
        action="store_true",
        help="запустить project_techcrunch_venture",
    )

    run_parser.add_argument(
        "--all",
        action="store_true",
        help="запустить все проекты через run_all.py",
    )

    alias_group = run_parser.add_argument_group("быстрые наборы project_twitter")
    for flag in SET_FLAGS:
        alias_group.add_argument(
            f"--{flag}",
            action="store_true",
            dest=f"set_{flag}",
            help=f"запустить Twitter-дайджест по набору {flag}",
        )

    return parser


def _gather_twitter_sets(args: argparse.Namespace) -> list[str]:
    return [
        SET_FLAGS[flag]
        for flag in SET_FLAGS
        if getattr(args, f"set_{flag}", False)
    ]


def _build_project_command(args: argparse.Namespace) -> list[str]:
    if args.twitter:
        if args.all:
            twitter_sets = list(SET_FLAGS.values())
        else:
            twitter_sets = _gather_twitter_sets(args)
        if not twitter_sets:
            raise ValueError("Добавьте хотя бы один флаг набора для --twitter")
        return [
            sys.executable,
            "project_twitter/main.py",
            "--set",
            ",".join(twitter_sets),
        ]

    if args.all:
        return [sys.executable, "run_all.py"]

    if args.a16z:
        return [sys.executable, "project_a16z/main.py"]
    if args.techcrunch_startup:
        return [sys.executable, "project_techcrunch_startup/main.py"]
    if args.techcrunch_venture:
        return [sys.executable, "project_techcrunch_venture/main.py"]

    raise ValueError("Ни один проект не выбран")


def main() -> None:
    ensure_venv()

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        if not (args.all or args.twitter or args.a16z or args.techcrunch_startup or args.techcrunch_venture):
            parser.error("нужно задать хотя бы один флаг: --all/--twitter/--a16z/--techcrunch_startup/--techcrunch_venture")

        cmd = _build_project_command(args)
        print("Запускаем:", " ".join(cmd))
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
