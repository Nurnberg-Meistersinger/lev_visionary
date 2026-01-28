"""
Telegram-бот для управления дайджестами.

Команды:
    /digest <set>  - запустить дайджест для набора (palantir, blockchain, etc.)
    /digest all    - топ-2 из каждой категории
    /sets          - показать доступные наборы
    /help          - справка

Запуск:
    python -m project_twitter.bot
"""
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import TELEGRAM_TOKEN, ADMIN_USER_ID
from accounts_loader import list_available_sets
from main import (
    process_set_async,
    process_all_sets_async,
    normalize_set_label,
)

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
    sets = [s for s in list_available_sets() if s != "all"]
    sets_list = ", ".join(sets)

    help_text = (
        "<b>📖 Команды бота</b>\n\n"
        "<b>/digest &lt;set&gt;</b> — запустить дайджест\n"
        f"  Доступные наборы: {sets_list}\n\n"
        "<b>/digest all</b> — топ-2 из каждой категории\n\n"
        "<b>/sets</b> — список наборов\n\n"
        "<b>/help</b> — эта справка"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


@admin_only
async def cmd_sets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать доступные наборы."""
    sets = list_available_sets()
    lines = ["<b>📋 Доступные наборы:</b>\n"]

    for s in sets:
        label = normalize_set_label(s)
        lines.append(f"• <code>{s}</code> — {label}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


@admin_only
async def cmd_digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запустить дайджест для указанного набора."""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажи набор: /digest palantir\n"
            "Или /digest all для всех категорий\n"
            "Список наборов: /sets"
        )
        return

    set_name = context.args[0].lower()
    available = list_available_sets()

    if set_name not in available:
        await update.message.reply_text(
            f"❌ Набор '{set_name}' не найден\n"
            f"Доступные: {', '.join(available)}"
        )
        return

    # Отправляем статус
    status_msg = await update.message.reply_text(
        f"⏳ Запускаю дайджест: {normalize_set_label(set_name)}..."
    )

    try:
        if set_name == "all":
            await process_all_sets_async()
        else:
            await process_set_async(set_name, top_n=10)

        await status_msg.edit_text(
            f"✅ Дайджест {normalize_set_label(set_name)} отправлен в канал!"
        )
    except Exception as e:
        logger.error(f"Digest error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Ошибка: {e}")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Приветствие при /start."""
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ Бот доступен только администратору")
        return

    await update.message.reply_text(
        "👋 Привет! Я бот для Twitter-дайджестов.\n"
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

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("sets", cmd_sets))
    app.add_handler(CommandHandler("digest", cmd_digest))

    # Запускаем polling
    print("✅ Бот запущен. Ожидание команд...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
