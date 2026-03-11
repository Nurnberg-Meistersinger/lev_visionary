"""
Telegram-бот для управления дайджестами.

Команды дайджестов:
    /digest <project>  - запустить проект (twitter:palantir, a16z, techcrunch_startup, etc.)
    /digest all        - топ-2 из каждой категории Twitter
    /projects          - список доступных проектов
    /help              - справка

Управление кастомными сетами:
    /newset <name> handle1 handle2 ...  - создать новый кастомный сет
    /addto <name> handle1 handle2 ...   - добавить аккаунты в кастомный сет
    /delset <name>                      - удалить кастомный сет

Запуск:
    python -m project_twitter.bot
"""
import logging
import asyncio
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from .config import TELEGRAM_TOKEN, ADMIN_USER_ID
from .accounts_loader import (
    list_available_sets,
    is_custom_set,
    create_custom_set,
    add_to_custom_set,
    delete_custom_set,
)
from .main import (
    process_set_async,
    process_all_sets_async,
    normalize_set_label,
)

# Добавляем корневую директорию в sys.path для импорта других проектов
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def admin_only(func):
    """Декоратор для ограничения доступа только админу."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != ADMIN_USER_ID:
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            await update.message.reply_text("⛔ Доступ запрещён")
            return
        return await func(update, context)
    return wrapper


@admin_only
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать справку."""
    help_text = (
        "<b>📖 Команды бота</b>\n\n"
        "<b>Дайджесты:</b>\n"
        "<b>/digest &lt;project&gt;</b> — запустить проект:\n"
        "  • Twitter: palantir, blockchain, venture, etc.\n"
        "  • Другие: a16z, techcrunch_startup, techcrunch_venture\n"
        "<b>/digest all</b> — топ-2 из каждой категории Twitter\n\n"
        "<b>Кастомные сеты:</b>\n"
        "<b>/newset &lt;name&gt; handle1 handle2 ...</b> — создать новый сет\n"
        "<b>/addto &lt;name&gt; handle1 handle2 ...</b> — добавить аккаунты в сет\n"
        "<b>/delset &lt;name&gt;</b> — удалить кастомный сет\n\n"
        "<b>/projects</b> — список всех проектов\n"
        "<b>/help</b> — эта справка\n\n"
        "<i>Примеры:</i>\n"
        "<code>/digest palantir</code>\n"
        "<code>/digest a16z</code>\n"
        "<code>/digest all</code>\n"
        "<code>/newset crypto_gurus elonmusk naval balajis</code>\n"
        "<code>/addto crypto_gurus pmarca</code>\n"
        "<code>/delset crypto_gurus</code>"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


@admin_only
async def cmd_projects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать доступные проекты."""
    sets = [s for s in list_available_sets() if s != "all"]
    builtin_sets = [s for s in sets if not is_custom_set(s)]
    custom_sets = [s for s in sets if is_custom_set(s)]

    lines = ["<b>📋 Доступные проекты:</b>\n", "<b>Twitter наборы (встроенные):</b>"]
    for s in builtin_sets:
        label = normalize_set_label(s)
        lines.append(f"  • <code>{s}</code> — {label}")

    if custom_sets:
        lines.append("\n<b>Twitter наборы (кастомные):</b>")
        for s in custom_sets:
            label = normalize_set_label(s)
            lines.append(f"  • <code>{s}</code> — {label}")

    lines.append("\n<b>Другие проекты:</b>")
    lines.append("  • <code>a16z</code> — a16z Daily Newsletter")
    lines.append("  • <code>techcrunch_startup</code> — TechCrunch Startups")
    lines.append("  • <code>techcrunch_venture</code> — TechCrunch Venture")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def run_other_project(project_name: str) -> None:
    """Запустить проект a16z/techcrunch."""
    import importlib.util

    main_path = project_root / project_name / "main.py"
    project_dir = str(project_root / project_name)

    # Временно добавляем директорию проекта в sys.path,
    # чтобы bare-импорты внутри main.py (from rss_reader import ...)
    # работали так же, как при прямом запуске python main.py
    sys.path.insert(0, project_dir)
    try:
        spec = importlib.util.spec_from_file_location(
            f"{project_name}_main", main_path
        )
        project_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(project_module)

        if asyncio.iscoroutinefunction(project_module.run):
            await project_module.run()
        else:
            # Если функция синхронная, запускаем в отдельном потоке
            await asyncio.to_thread(project_module.run)
    finally:
        if project_dir in sys.path:
            sys.path.remove(project_dir)


@admin_only
async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запустить дайджест для указанного проекта."""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажи проект: /digest palantir\n"
            "Или: /digest a16z\n"
            "Или: /digest all (Twitter топ-2)\n"
            "Список проектов: /projects"
        )
        return

    project_name = context.args[0].lower()

    # Список доступных Twitter-сетов
    twitter_sets = list_available_sets()

    # Список других проектов
    other_projects = {
        "a16z": "project_a16z",
        "techcrunch_startup": "project_techcrunch_startup",
        "techcrunch_venture": "project_techcrunch_venture",
    }

    # Отправляем статус
    status_msg = await update.message.reply_text(f"⏳ Запускаю: {project_name}...")

    try:
        # Twitter проекты
        if project_name in twitter_sets:
            if project_name == "all":
                await process_all_sets_async()
                await status_msg.edit_text("✅ Twitter топ-2 из каждой категории отправлен!")
            else:
                await process_set_async(project_name, top_n=10)
                await status_msg.edit_text(
                    f"✅ Дайджест {normalize_set_label(project_name)} отправлен в канал!"
                )

        # Другие проекты (a16z, techcrunch)
        elif project_name in other_projects:
            module_name = other_projects[project_name]
            await run_other_project(module_name)
            await status_msg.edit_text(f"✅ Проект {project_name} выполнен!")

        else:
            await status_msg.edit_text(
                f"❌ Проект '{project_name}' не найден\n"
                f"Используй /projects для списка"
            )

    except Exception as e:
        logger.error(f"Digest error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Ошибка: {e}")


@admin_only
async def cmd_newset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Создать новый кастомный набор аккаунтов."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Использование: /newset &lt;название&gt; @handle1 handle2 ...\n"
            "Пример: <code>/newset crypto_gurus elonmusk naval balajis</code>",
            parse_mode="HTML"
        )
        return

    set_name = context.args[0].lower()
    handles = context.args[1:]

    try:
        data = create_custom_set(set_name, handles)
        handles_list = "\n".join(f"  • @{acc['handle']}" for acc in data["accounts"])
        await update.message.reply_text(
            f"✅ Сет <b>{data['name']}</b> создан!\n\n"
            f"Аккаунты ({len(data['accounts'])}):\n{handles_list}\n\n"
            f"Запустить: <code>/digest {set_name}</code>",
            parse_mode="HTML"
        )
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}")


@admin_only
async def cmd_addto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавить аккаунты в существующий кастомный сет."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Использование: /addto &lt;название&gt; @handle1 handle2 ...\n"
            "Пример: <code>/addto crypto_gurus pmarca</code>",
            parse_mode="HTML"
        )
        return

    set_name = context.args[0].lower()
    handles = context.args[1:]

    try:
        data, added = add_to_custom_set(set_name, handles)
        added_list = "\n".join(f"  • @{acc['handle']}" for acc in added)
        await update.message.reply_text(
            f"✅ Добавлено в <b>{data['name']}</b> ({len(added)}):\n{added_list}\n\n"
            f"Всего аккаунтов в сете: {len(data['accounts'])}",
            parse_mode="HTML"
        )
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}")


@admin_only
async def cmd_delset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удалить кастомный набор аккаунтов."""
    if not context.args:
        await update.message.reply_text(
            "❌ Использование: /delset &lt;название&gt;\n"
            "Пример: <code>/delset crypto_gurus</code>",
            parse_mode="HTML"
        )
        return

    set_name = context.args[0].lower()

    try:
        delete_custom_set(set_name)
        await update.message.reply_text(
            f"✅ Сет <b>{set_name}</b> удалён",
            parse_mode="HTML"
        )
    except ValueError as e:
        await update.message.reply_text(f"❌ {e}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие при /start."""
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Бот доступен только администратору")
        return

    await update.message.reply_text(
        "👋 Привет! Я бот для запуска всех дайджестов:\n"
        "• Twitter (Palantir, Blockchain, Venture и др.)\n"
        "• a16z Daily Newsletter\n"
        "• TechCrunch Startups & Venture\n\n"
        "Используй /help для списка команд."
    )


def main() -> None:
    """Запуск бота."""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не задан в .env")

    if not ADMIN_USER_ID:
        raise ValueError("ADMIN_USER_ID не задан в .env")

    print("🤖 Запуск Telegram-бота...")

    # Создаём приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(CommandHandler("digest", cmd_digest))
    app.add_handler(CommandHandler("newset", cmd_newset))
    app.add_handler(CommandHandler("addto", cmd_addto))
    app.add_handler(CommandHandler("delset", cmd_delset))

    # Запускаем polling
    print("✅ Бот запущен. Ожидание команд...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
