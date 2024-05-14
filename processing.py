#!/usr/bin/env python
import datetime
import pathlib
import re
import subprocess
import time
from urllib.parse import urlparse

import requests
import yaml
from slugify import slugify
from telegram import Update, InputMediaAudio, InputFile
from telegram.ext import ContextTypes

from audio import get_song_duration
from ytb import parse_input, get_movie_id

WHERE_ALL_STORES = 'storeTelegramChats'
DEBUG = True
DEBUG_SAVE_RAW_DATA = True


def cleanTitleWithPattern(text, pattern):
    if match := re.match(pattern, text):
        to_replace = match.group(1)
        return text.replace(to_replace, '')

    return text


def cleanTitleAllPatterns(text, patterns):
    for pattern in patterns:
        text = cleanTitleWithPattern(text, pattern)
    return text


def chat_title_clean(title: str = '', pattern: str = 'U(u*)-u'):
    """
    Return all parts of remain after cutting Uuuuuu-uu
    (1)(Uuuuu-u)(2)
    :param pattern:
    :param title:
    :return:
    """
    res = re.search(pattern, title)
    if not res:
        return slugify(title)

    parts = [slugify(title[:res.span()[0]]), slugify(title[res.span()[1]:])]

    return parts


def get_dynamic_filename(
        prefix: str = '',
        dynamic_text: str = '',
        suffix: str = '',
        max_length: int = 16) -> str:
    """

    :param prefix:
    :param dynamic_text:
    :param suffix:
    :param max_length:
    :return:
    """
    words = slugify(dynamic_text).split('-')
    small_name = ''

    local_max_length = max_length - len(prefix) - len(suffix)
    for index in range(len(words)):
        if index == 0:
            if len(words[index]) > local_max_length:
                small_name = words[index][:local_max_length]
                break
            else:
                small_name = words[index]
                continue

        proposed_name = f'{small_name}-{words[index]}'
        if len(proposed_name) > local_max_length:
            break

        small_name = proposed_name

    return f'{prefix}{small_name}{suffix}'


def chat_id_sanitize(
        chat_id_original: str,
        prefix_chat_id_to_remove: str = '-100') -> str:

    """

    :param chat_id_original:
    :param prefix_chatid_to_remove:
    :return:
    """
    if not chat_id_original.startswith("-"):
        return chat_id_original

    if chat_id_original.startswith(prefix_chat_id_to_remove):
        return chat_id_original.removeprefix(prefix_chat_id_to_remove)

    return chat_id_original


def message_text_filter(text: str = '') -> str:

    text = text.replace("\\", "")
    text = f'\n{text}\n'

    return text


from pytube import YouTube


def download_thumbnail(youtube_url, output_path):
    try:
        yt = YouTube(youtube_url)
        print('yt.thumbnail_url: ', yt.thumbnail_url)

        try:
            response = requests.get(yt.thumbnail_url)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print("Image downloaded successfully")
            else:
                print("Failed to download image. Status code:", response.status_code)
        except Exception as e:
            print("An error occurred:", str(e))

        print("Thumbnail downloaded successfully!")

    except Exception as e:
        print(f"Error downloading thumbnail: {str(e)}")


def filter_text(text):
    pattern = r'[^a-zA-Z0-9\s]'
    return re.sub(pattern, '', text)


async def make_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('🍎 Update Processing: ')
    print(yaml.dump(update, default_flow_style=False))
    print()

    print('🕔 Time: ', datetime.datetime.now().strftime("%H:%M:%S"))
    print()

    if not update.message.text:
        print('⛔️ no update.message.text')
        return

    if not urlparse(update.message.text).netloc:
        print('⛔️ No URL in your request!')
        return

    url, discovered_word = parse_input(update.message.text)
    if not url:
        print('⛔️ Bad input URL. Check it!')
        return

    if not (movie_id := get_movie_id(url)):
        print('⛔️ Couldnt parse movie id from your URL. Check it!')
        return

    post = await context.bot.send_message(
        chat_id=update.message.from_user.id,
        reply_to_message_id=update.message.id,
        text='🟩 Starting'
    )
    print('Post: ', post.id)

    data_dir = pathlib.Path('data')
    opus_file = data_dir.joinpath(f'{movie_id}.opus')

    post_text = ''
    if not opus_file.exists():
        output = opus_file.with_suffix('').as_posix()
        command = f'yt-dlp --extract-audio --output {output} {url}'
        print('❤️ ', command)
        print()

        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        rows = []
        for line in process.stdout:
            print(line.strip())
            rows.append(line.strip())

            full_text = f'🟩 Downloading: ({movie_id})\n\n' + '\n'.join(rows[-6:]).replace('https://www.youtube.com/', '')
            if full_text != post.text:
                try:
                    await post.edit_text(full_text)
                except Exception as e:
                    print('Some Error')
            post_text = full_text

    if not opus_file.exists():
        await post.edit_text(f'{post_text} \n\n 🟥 Unexpected error. [not opus_file.exists()].')
        return

    await post.edit_text(f'🟩 Compressing and Converting to .m4a: ({movie_id}) \n ... ')

    m4a_file = data_dir.joinpath(f'{movie_id}.m4a')

    if not m4a_file.exists():
        command = f'ffmpeg -i {opus_file.as_posix()} -c:a aac -b:a 48k {m4a_file.as_posix()}'
        print('❤️ ', command)
        print()

        process = subprocess.Popen(
            command.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

        rows = []
        for line in process.stdout:
            print(line.strip())
            rows.append(line.strip())

            full_text = f'🟩 Compressing and Converting to .m4a: ({movie_id})\n\n' + '\n'.join(rows[-6:])
            if full_text != post.text:
                try:
                    await post.edit_text(full_text)
                except Exception as e:
                    print('Some Error')
            post_text = full_text

    if not m4a_file.exists():
        await post.edit_text(f'{post_text} \n\n 🟥 Unexpected error. [not m4a_file.exists()].')
        return

    opus_file.unlink()

    thumbnail_file = data_dir.joinpath(f'{movie_id}.jpg')
    if not thumbnail_file.exists():
        download_thumbnail(url, thumbnail_file.as_posix())

    if not thumbnail_file.exists():
        await post.edit_text(f'{post_text} \n\n 🟥 Unexpected error. [not thumbnail_file.exists()].')

    await post.edit_text('🟩 Add Cover to m4a \n ... ')
    if True:
        # Adding cover to m4a
        command = f'mp4art --add {thumbnail_file.as_posix()} {m4a_file.as_posix()}'
        print('❤️ ', command)
        print()

        process = subprocess.Popen(
            command.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

    print('🟩 Uploading to Telegram')
    await post.edit_text('🟩 Uploading to Telegram \n ... ')

    print('🟩 Before: putybe \n ... ')
    import ssl
    ssl._create_default_https_context = ssl._create_stdlib_context
    yt = YouTube(url)

    filename = re.sub(r'[^\w\s\-\_]', ' ', yt.title).replace('  ', ' ').strip()
    await context.bot.send_audio(
        chat_id=update.message.chat_id,
        audio=m4a_file.as_posix(),
        reply_to_message_id=update.message.id,
        thumbnail=thumbnail_file.open('rb'),
        duration=get_song_duration(m4a_file),
        filename=f'{filename}.m4a',
        caption=yt.title
    )

    await post.edit_text('🟩 Success!')
    time.sleep(1)
    await post.delete()

    print('🟩 End')









