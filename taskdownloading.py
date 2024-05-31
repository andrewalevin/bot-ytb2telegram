# huey = SqliteHuey(filename='huey-queue.db')
import asyncio
import json
import pathlib
import subprocess
import time

import dramatiq
import nest_asyncio
from dramatiq.brokers.redis import RedisBroker
from mutagen.mp4 import MP4
from telegram import Bot
from telegram.ext import ContextTypes

import config
import config_token
from token_telegram_bot import get_running_mode
from utils_downloading import download_thumbnail, time_format, output_filename_in_telegram, make_split

redis_broker = RedisBroker()
dramatiq.set_broker(redis_broker)

nest_asyncio.apply()


def list_scheduled_tasks():
    return redis_broker.zrange('dramatiq:default:deferred', 0, -1)


async def task_download(chat_id, message_id, url, movie_id, post_status_id, opt_split_minutes):
    print('🦀 Task Download start: ', movie_id)
    print('📚 Tasks: ')
    for task in list_scheduled_tasks():
        print('🦆 Task: ', json.loads(task))
    print()

    running_mode = get_running_mode()
    token = config_token.RUNNING_MODE_CONFIG_SENSITIVE[running_mode]['token']
    bot = Bot(token=token)

    log_text_top = f'⌛️ Downloading: ({movie_id})\n\n'
    await bot.editMessageText(
        chat_id=chat_id,
        message_id=post_status_id,
        text=log_text_top
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
        log_last_text = ''
        for line in process.stdout:
            print(line.strip())
            log_rows.append(line.strip())

            log_text = log_text_top + '\n'.join(log_rows[-config.LOG_ROWS_COUNT:]) + '\n ... '
            log_text = log_text.replace('https://youtu.be/', '').replace('https://www.youtube.com/', '')

            if log_text == log_last_text:
                continue

            try:
                await bot.editMessageText(
                    chat_id=chat_id,
                    message_id=post_status_id,
                    text=log_text
                )
                log_last_text = log_text
            except Exception as e:
                print('Some Error')

    if not m4a_file.exists():
        await bot.editMessageText(
            chat_id=chat_id,
            message_id=post_status_id,
            text=f'🟥 Unexpected error in yt-dlp. [not m4a_file.exists()].\n\n {log_text}'
        )
        return

    try:
        audio = MP4(m4a_file.as_posix())
    except Exception as e:
        return str(e)

    if not audio:
        await bot.editMessageText(
            chat_id=chat_id,
            message_id=post_status_id,
            text='🟥 Unexpected error. [not audio in MP4 metadata].'
        )
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
        await bot.editMessageText(
            chat_id=chat_id,
            message_id=post_status_id,
            text=f'🟥 One problem. [not thumbnail_file.exists()]. Continue'
        )
        time.sleep(3)

    m4a_objs = []
    if duration_seconds > config.SPLIT_THRESHOLD_MINUTES * 60:
        opt_split_minutes = config.SPLIT_AUDIO_DURATION_MINUTES

    if opt_split_minutes:
        print('⌛ Splitting ... ')
        await bot.editMessageText(
            chat_id=chat_id,
            message_id=post_status_id,
            text='⌛ Splitting \n ... '
        )

        m4a_parts = make_split(m4a_file, duration_seconds, opt_split_minutes, config.SPLIT_DELTA_SECONDS)
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
                    await bot.editMessageText(
                        chat_id=chat_id,
                        message_id=post_status_id,
                        text=f'🟥 Error [not (file := m4a_obj.get]'
                    )
                    return

                print(f'🔹 {file.name}')
                if not file.exists():
                    print(f'🟥 {file.name} This File Unexpected exists!')
                    await bot.editMessageText(
                        chat_id=chat_id,
                        message_id=post_status_id,
                        text=f'🟥 {file.name} This File Unexpected exists!'
                    )
                    return
        else:
            m4a_objs = [{'file': m4a_file, 'duration': duration_seconds}]
    else:
        m4a_objs = [{'file': m4a_file, 'duration': duration_seconds}]

    print('⌛ Uploading to Telegram')
    await bot.editMessageText(
        chat_id=chat_id,
        message_id=post_status_id,
        text='⌛ Uploading to Telegram \n ... '
    )

    for idx, obj in enumerate(m4a_objs, start=1):
        reply_to_message_id = message_id
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

        await bot.send_audio(
            chat_id=chat_id,
            reply_to_message_id=reply_to_message_id,
            audio=file,
            duration=duration,
            filename=filename,
            thumbnail=thumbnail,
            caption=caption
        )

    await bot.delete_message(chat_id=chat_id,message_id=post_status_id)

    print('👍 Success!')
    if len(m4a_objs) > 1:
        for obj in m4a_objs:
            file = obj.get('file')
            file.unlink()

    print()


@dramatiq.actor
def task_downloading_container(chat_id, message_id, url, movie_id, post_status_id, opt_split_minutes):
    print('🍎 task_downloading_container: ')
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(task_download(chat_id, message_id, url, movie_id, post_status_id, opt_split_minutes))
    loop.run_until_complete(future)
    result = future.result()

    print('🍎 After asyncio in task')