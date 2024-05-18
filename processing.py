#!/usr/bin/env python

import pathlib
import re
import ssl
import subprocess
import time
from datetime import timedelta
from urllib.parse import urlparse

import requests
from mutagen.mp4 import MP4
from telegram import Update
from telegram.ext import ContextTypes

from audio_parts import get_splitting_parts
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


def showtime(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}:{minutes}:{seconds}'


def make_split(audio_file,  audio_duration, split_minutes, delta_seconds=0):
    split_minutes = int(split_minutes)

    if not isinstance(split_minutes, int):
        return
    if split_minutes <= 0:
        return
    if split_minutes > 241:
        split_minutes = 241

    print('🦀 Splitting: ', split_minutes)

    parts = get_splitting_parts(audio_length=audio_duration, duration=split_minutes * 60, delta=delta_seconds)
    print([[showtime(part[0]), showtime(part[1])] for part in parts])

    if len(parts) < 2:
        return

    print('🦀 Make Splitting: ')
    return parts
    # return [audio_file.with_name(f'{audio_file.stem}-p{idx}-of{len((parts))}.m4a') for idx, part in enumerate(parts, start=1)]


def time_format(seconds):
    if not isinstance(seconds, int):
        print('🛑 time_format(): Variable is not int')
        return '00:00:00'
    if seconds < 0:
        print('🛑 time_format(): Variable is < 0 ')
        return '00:00:00'

    return '{:0>8}'.format(str(timedelta(seconds=int(seconds))))


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

    split_minutes = 0
    if match := re.search(r'split=(\d+)', update.message.text):
        if value := int(match.group(1)):
            print('🦀 Split ', match)
            split_minutes = value

    log_text_top = f'⌛️ Downloading: ({movie_id})\n\n'
    post_status = await context.bot.send_message(
        chat_id=update.message.from_user.id,
        reply_to_message_id=update.message.id,
        text=log_text_top + ' ... '
    )

    data_dir = pathlib.Path(config.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    m4a_file = data_dir.joinpath(f'{movie_id}.m4a')

    if not m4a_file.exists():
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

            if log_text == post_status.text:
                continue

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

    if not thumbnail_file.exists():
        await post_status.edit_text(f'🟥 One problem. [not thumbnail_file.exists()]. Continue')
        time.sleep(3)

    m4a_objs = []
    if duration_seconds > config.SPLIT_THRESHOLD_MINUTES * 60:
        split_minutes = config.SPLIT_AUDIO_DURATION_MINUTES

    if split_minutes:
        print('⌛ Splitting ... ')
        await post_status.edit_text('⌛ Splitting \n ... ')

        m4a_parts = make_split(m4a_file,  duration_seconds, split_minutes, config.SPLIT_DELTA_SECONDS)
        print('m4a_parts: ', m4a_parts)
        if m4a_parts:
            cmds_list = []
            for idx, part in enumerate(m4a_parts, start=1):
                output_file = m4a_file.with_stem(f'{m4a_file.stem}-p{idx}-of{len(m4a_parts)}')
                m4a_objs.append({'file': output_file, 'duration': part[1] - part[0]})
                #   https://www.youtube.com/watch?v=HlwTLyfB3QU
                cmd = f'ffmpeg -i {m4a_file.as_posix()} -ss {time_format(part[0])} -to {time_format(part[1])} -c copy -y {output_file.as_posix()}'
                print(cmd)
                cmds_list.append(cmd.split(' '))

            processes = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in cmds_list]

            for idx, process in enumerate(processes):
                print('🔹 Process, ', idx)
                process.wait()

            print("🟢 All Done! Lets see .m4a files and their length")
            for m4a_obj in m4a_objs:
                if not (file := m4a_obj.get('file')):
                    print(f'🟥 Error. [not (file := m4a_obj.get]')
                    await post_status.edit_text(f'🟥 Error [not (file := m4a_obj.get]')
                    return

                print(f'🔹 {file.name}')
                if not file.exists():
                    print(f'🟥 {file.name} This File Unexpected exists!')
                    await post_status.edit_text(f'🟥 {file.name} This File Unexpected exists!')
                    return
        else:
            m4a_objs = [{'file': m4a_file, 'duration': duration_seconds}]
    else:
        m4a_objs = [{'file': m4a_file, 'duration': duration_seconds}]

    print('⌛ Uploading to Telegram')
    await post_status.edit_text('⌛ Uploading to Telegram \n ... ')

    for idx, obj in enumerate(m4a_objs, start=1):
        reply_to_message_id = update.message.id
        if idx > 1:
            reply_to_message_id = None

        file = obj.get('file')
        filename = output_filename_in_telegram(title)
        caption = title
        duration = obj.get('duration')
        thumbnail = thumbnail_file.open('rb')

        if len(m4a_objs) > 1:
            filename = f'(p{idx}-of{len(m4a_objs)}) {filename}'
            caption = f'[Part {idx} of {len(m4a_objs)}] {title}'

        await context.bot.send_audio(
            chat_id=update.message.chat_id,
            reply_to_message_id=reply_to_message_id,
            audio=file,
            duration=duration,
            filename=filename,
            thumbnail=thumbnail,
            caption=caption
        )

    await post_status.delete()

    print('👍 Success!')
    if len(m4a_objs) > 1:
        for obj in m4a_objs:
            file = obj.get('file')
            file.unlink()

    print()









