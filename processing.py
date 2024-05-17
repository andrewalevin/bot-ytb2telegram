#!/usr/bin/env python

import pathlib
import re
import ssl
import subprocess
import time
from urllib.parse import urlparse

import requests
import yaml
from mutagen.mp4 import MP4
from telegram import Update
from telegram.ext import ContextTypes
from ytb import parse_input, get_movie_id
import config
from pytube import YouTube


def download_thumbnail(youtube_url, output_path):
    ssl._create_default_https_context = ssl._create_stdlib_context
    try:
        yt = YouTube(youtube_url)
        print('🍏 yt.thumbnail_url: ', yt.thumbnail_url)

        try:
            response = requests.get(yt.thumbnail_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
            else:
                print("Failed to download image. Status code:", response.status_code)
        except Exception as e:
            print("An error occurred:", str(e))

    except Exception as e:
        print(f"Error downloading thumbnail: {str(e)}")


def output_filename_in_telegram(text):
    name = (re.sub(r'[^\w\s\-\_\(\)\[\]]', ' ', text)
                .replace('    ', ' ')
                .replace('   ', ' ')
                .replace('  ', ' ')
                .strip())

    return f'{name}.m4a'


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

    if not (movie_id := get_movie_id(url)):
        print('⛔️ Not a Youtube Url. Skip.')
        return

    log_text_top = f'⌛️ Downloading: ({movie_id})\n\n'
    post_status = await context.bot.send_message(
        chat_id=update.message.from_user.id,
        reply_to_message_id=update.message.id,
        text=log_text_top + ' ... '
    )

    data_dir = pathlib.Path(config.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    m4a_file = data_dir.joinpath(f'{movie_id}.m4a')

    command = f'yt-dlp {config.YT_DLP_OPTIONS_DEFAULT} --output {m4a_file.as_posix()} {url}'
    print('❤️ BASH: ', command)
    process = subprocess.Popen(
        command.split(' '),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)

    log_rows = []
    log_text = ''
    for line in process.stdout:
        print(line.strip())
        log_rows.append(line.strip())

        log_text = log_text_top + '\n'.join(log_rows[-config.LOG_ROWS_COUNT:]) + '\n ... '
        log_text = log_text.replace('https://youtu.be/', '').replace('https://www.youtube.com/', '')

        if log_text != post_status.text:
            try:
                await post_status.edit_text(log_text)
            except Exception as e:
                print('Some Error')

    if not m4a_file.exists():
        await post_status.edit_text(f'🟥 Unexpected error in yt-dlp. [not m4a_file.exists()].\n\n {log_text}')
        return

    try:
        audio = MP4(m4a_file.as_posix())
    except Exception as e:
        return str(e)

    if not audio:
        await post_status.edit_text('🟥 Unexpected error. [not audio in MP4 metadata].')
        return

    title = str(movie_id)
    if audio.get('\xa9nam'):
        title = audio.get('\xa9nam')[0]

    duration_seconds = None
    if audio.info.length:
        duration_seconds = int(audio.info.length)

    thumbnail_file = data_dir.joinpath(f'{movie_id}.jpg')
    if not thumbnail_file.exists():
        download_thumbnail(url, thumbnail_file.as_posix())

    thumbnail = None
    if thumbnail_file.exists():
        thumbnail = thumbnail_file.open('rb')
    else:
        await post_status.edit_text(f'🟥 One problem. [not thumbnail_file.exists()]. Continue')
        time.sleep(3)

    print('⌛ Uploading to Telegram')
    await post_status.edit_text('⌛ Uploading to Telegram \n ... ')

    await context.bot.send_audio(
        chat_id=update.message.chat_id,
        audio=m4a_file.as_posix(),
        reply_to_message_id=update.message.id,
        duration=duration_seconds,
        filename=output_filename_in_telegram(title),
        thumbnail=thumbnail,
        caption=title
    )

    await post_status.delete()

    print('👍 Success!')
    print()









