#!/usr/bin/env python

import re
import time
from urllib.parse import urlparse

from dramatiq import Middleware, Broker
from telegram import Update
from telegram.ext import ContextTypes

from taskdownloading import task_download, task_downloading_container
from url_parser import get_youtube_id, parse_input


class ScheduledTaskCounter(Middleware):
    def __init__(self):
        super().__init__()
        self.scheduled_task_count = 0

    def after_enqueue(self, broker, message, sender):
        if message.queue_name.startswith("dramatiq:scheduled:"):
            self.scheduled_task_count += 1


def get_scheduled_tasks_count():
    broker = Broker(middlewares=[ScheduledTaskCounter()])

    return broker.middleware[0].scheduled_task_count


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

    log_text_top = f'⌛️ Queued: ({movie_id})\n\n'
    post_status = await context.bot.send_message(
        chat_id=update.message.from_user.id,
        reply_to_message_id=update.message.id,
        text=log_text_top + ' ... '
    )

    time.sleep(1)
    task_downloading_container.send(update.message.from_user.id, update.message.id, url, movie_id, post_status.id, opt_split_minutes)

    print('Tasks: ', get_scheduled_tasks_count())

    print('💚 After call task: ', movie_id)











