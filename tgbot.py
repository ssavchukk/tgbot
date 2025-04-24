import re
import logging
import unicodedata
from telegram.ext import Application, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

# Токен вашего бота
TOKEN = "7794147282:AAFhJFb2fTvVgQxzy20oehf7S0rV6hIF4dk"

# Настраиваем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def clean_text(text):
    return ''.join(c for c in text if not unicodedata.category(c).startswith('Cf'))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    logger.info(f"Получено сообщение: {message_text[:50]}...")

    if re.match(r'(?i)^\s*.*?баланс.*?', message_text):
        logger.info("Сообщение распознано как баланс")
        await process_balance_message(update, message_text)
    elif re.match(r'(?i)^\s*.*?ура(?:а+)?\s*.*?', message_text):
        logger.info("Сообщение распознано как розыгрыш")
        await process_lottery_message(update, message_text)
    else:
        logger.info("Сообщение не распознано")
        await update.message.reply_text(
            "Сообщение не распознано. Убедитесь, что оно начинается со слова 'БАЛАНС' или 'ура'."
        )


async def process_balance_message(update: Update, message_text: str):
    try:
        amounts = re.findall(r'-\s*([\d\s]+)\s*₽', message_text)
        logger.info(f"Найдено сумм: {len(amounts)}")

        total = 0
        for amount in amounts:
            cleaned_amount = amount.replace(" ", "")
            if cleaned_amount.isdigit():
                total += int(cleaned_amount)
            else:
                logger.warning(f"Невалидная сумма: {cleaned_amount}")

        response = f"💰 Общая сумма: {total}₽"
        logger.info(f"Результат: {response}")
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Ошибка в process_balance_message: {e}")
        await update.message.reply_text("Произошла ошибка при обработке баланса. Попробуйте ещё раз.")


async def process_lottery_message(update: Update, message_text: str):
    try:
        cleaned_message = clean_text(message_text)
        names = re.findall(r'@~\s*([^\n]+)', cleaned_message)
        logger.info(f"Найдено имен: {len(names)}")

        if not names:
            await update.message.reply_text("Не удалось найти имена участников. Убедитесь, что они следуют за '@~'.")
            return

        name_counts = {}
        for name in names:
            cleaned_name = name.strip()
            name_counts[cleaned_name] = name_counts.get(cleaned_name, 0) + 1

        response = ""
        for i, (name, count) in enumerate(name_counts.items(), 1):
            response += f"[{i}] @~{name} - {count}\n"

        logger.info("Отправка результата розыгрыша")
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Ошибка в process_lottery_message: {e}")
        await update.message.reply_text("Произошла ошибка при обработке розыгрыша. Попробуйте ещё раз.")


def main():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, handle_message))
        logger.info("Запуск бота...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка в main: {e}")


if __name__ == "__main__":
    main()
