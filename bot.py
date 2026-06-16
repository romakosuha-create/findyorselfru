# coding=utf-8
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# ============ НАСТРОЙКИ (ЗАПОЛНИ СВОИ) ============

BOT_TOKEN = "8324552891:AAFRj0eJsMnNN1b9O0kbFeTA_c-eNDX5e3A"

# username твоего бесплатного канала (без @)
FREE_CHANNEL = "consciouscivilization"

# Путь к PDF (файл должен называться book.pdf и лежать рядом с bot.py)
PDF_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book.pdf")

# Ссылки
FREE_CHANNEL_LINK = "https://t.me/consciouscivilization"
PAID_CHANNEL_LINK = "https://t.me/tribute/app?startapp=ep_8xrGGtPRQVTWbG7rUygNNEPWMg9KtQGNLXeP8HG5xiAyvmn4bL"

# ============ ТЕКСТЫ ============

WELCOME_TEXT = (
    "Привет 👋\n\n"
    "Я — бот Создателя.\n\n"
    "У меня для тебя книга «Карта ментальных тупиков» — "
    "8 лет поиска себя, сжатые в 20 минут чтения. "
    "Бесплатно.\n\n"
    "Чтобы получить её, подпишись на канал «Осознанная цивилизация» "
    "и нажми кнопку ниже."
)

NOT_SUBSCRIBED_TEXT = (
    "Ты пока не подписан на канал.\n\n"
    "Подпишись → потом нажми «Проверить подписку» ещё раз."
)

BOOK_SENT_TEXT = (
    "Вот твоя книга 📖\n\n"
    "Читай не спеша. Если после прочтения захочешь пойти глубже — "
    "в конце книги есть дверь.\n\n"
    "А пока — посты в канале помогут держать фокус на себе."
)

ERROR_TEXT = (
    "Что-то пошло не так. Попробуй позже или напиши @kosuhar."
)

# ============ ЛОГИКА ============

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=f"@{FREE_CHANNEL}", user_id=user_id
        )
        return member.status in ("member", "administrator", "creator")
    except TelegramError as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Подписаться на канал", url=FREE_CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_sub")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=get_main_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    is_subscribed = await check_subscription(user_id, context)

    if is_subscribed:
        try:
            with open(PDF_FILE_PATH, "rb") as f:
                await query.message.reply_document(
                    document=f,
                    filename="Карта_ментальных_тупиков.pdf",
                    caption=BOOK_SENT_TEXT
                )
        except FileNotFoundError:
            logger.error(f"Файл {PDF_FILE_PATH} не найден!")
            await query.message.reply_text(ERROR_TEXT)
    else:
        await query.message.reply_text(
            NOT_SUBSCRIBED_TEXT,
            reply_markup=get_main_keyboard()
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="check_sub"))

    logger.info("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()