#!/usr/bin/env python

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler
import config_token
from processing import make_audio
from token_telegram_bot import get_running_mode
import commands

if __name__ == '__main__':
    print('🚀 main.py')

    running_mode = get_running_mode()
    token = config_token.RUNNING_MODE_CONFIG_SENSITIVE[running_mode]['token']

    application = ApplicationBuilder().token(token).build()

    # commands.update_timers_for_all_users(application.job_queue)

    #application.add_handler(CommandHandler('start', commands.start_command))

    application.add_handler(CommandHandler("help", commands.help_command))

    # application.add_handler(CommandHandler("code", commands.code_check))
    #
    # application.add_handler(CommandHandler("code12", commands.invite_code_for_friends))
    #
    # application.add_handler(CommandHandler("dev", commands.dev_command))
    #
    # application.add_handler(CommandHandler("podcast_details", commands.podcast_details))
    #
    # application.add_handler(CommandHandler("podcast_annotate_details", commands.podcast_annotate_details))
    #
    # application.add_handler(conversation_main)
    #
    # application.add_handler(conv_handler_nested)

    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, make_audio))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


