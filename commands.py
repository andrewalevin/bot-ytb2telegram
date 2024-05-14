
from telegram import Update, Message
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, JobQueue

import config


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=config.HELP_TEXT,
        parse_mode=ParseMode.HTML
    )

