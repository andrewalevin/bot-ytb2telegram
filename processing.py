#!/usr/bin/env python
import pathlib
import re
import time
from urllib.parse import urlparse

import huey
from dramatiq import Middleware, Broker
from telegram import Update
from telegram.ext import ContextTypes

from taskdownloading import task_download
from url_parser import get_youtube_id, parse_input


class ScheduledTaskCounter(Middleware):
    def __init__(self):
        super().__init__()
        self.scheduled_task_count = 0

    def after_enqueue(self, broker, message, sender):
        if message.queue_name.startswith("dramatiq:scheduled:"):
            self.scheduled_task_count += 1


def get_scheduled_tasks_count():
    pending_tasks = huey.pending()
    for task in pending_tasks:
        print(f'Task ID: {task.id}, Task Data: {task.data}')


async def make_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text:
        print('⛔️ No update.message.text. Skip.')
        return

    if not urlparse(update.message.text).netloc:
        print('⛔️ No URL! Skip.')
        return

    url, discovered_word = parse_input(update.message.text)
    if not url:
        print('⛔️ Bad URL. Skip.')
        return

    if not (movie_id := get_youtube_id(url)):
        print('⛔️ Not a Youtube Url. Skip.')
        return

    opt_split_minutes = 0
    if match := re.search(r'split=(\d+)', update.message.text):
        if value := int(match.group(1)):
            print('🦀 Split ', match)
            opt_split_minutes = value

    post_status = await context.bot.send_message(
        chat_id=update.message.from_user.id,
        reply_to_message_id=update.message.id,
        text=f'⌛️ Downloading: \n ... '
    )

    task_message = task_download.send(movie_id, opt_split_minutes)

    #todo
    data = task_message.get_result(block=True, timeout=100000)
    print('🚛 DATA: ', data)
    print()

    if data.get('error'):
        print('🍒 Make error log')
        with pathlib.Path(data.get('log')).open('r') as log_file:
            text = data.get('error') + '\n\n' + log_file.read()
            await post_status.edit_text(text)
            return

    await post_status.edit_text('⌛ Uploading to Telegram \n ... ')

    for idx, audio in enumerate(data.get('audios'), start=1):
        with pathlib.Path(data.get('thumbnail')).open('rb') as thumbnail_file:
            await context.bot.send_audio(
                chat_id=update.message.from_user.id,
                reply_to_message_id=None if idx > 1 else update.message.id,
                audio=audio.get('path'),
                duration=audio.get('duration'),
                filename=audio.get('filename'),
                thumbnail=thumbnail_file,
                caption=audio.get('caption')
            )

        await post_status.delete()

    print('💚 After call task: ', movie_id)











