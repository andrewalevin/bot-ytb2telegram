#!/usr/bin/env python
import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
import config_token
from processing import make_audio
from token_telegram_bot import get_running_mode
import commands


def main():
    print('🚀 main.py')

    running_mode = get_running_mode()
    token = config_token.RUNNING_MODE_CONFIG_SENSITIVE[running_mode]['token']

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("help", commands.help_command))

    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, make_audio, block=False))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()


