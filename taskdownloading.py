
import pathlib
import subprocess

import dramatiq
import nest_asyncio
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AsyncIO
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend
from mutagen.mp4 import MP4

import config
from utils_downloading import download_thumbnail, time_format, make_split, output_filename_in_telegram
from huey import SqliteHuey

redis_broker = RedisBroker()
redis_broker.add_middleware(AsyncIO())

result_backend = RedisBackend(url="redis://localhost:6379/0")

redis_broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(redis_broker)

nest_asyncio.apply()

#   huey = SqliteHuey(filename='huey-table.db')

#   @huey.task()


@dramatiq.actor(store_results=True)
async def task_download(movie_id, opt_split_minutes):
    print('🦀 Task Download start: ', movie_id)

    context = dict()
    context['error'] = ''
    context['log'] = ''
    context['audios'] = []
    context['thumbnail'] = ''

    data_dir = pathlib.Path(config.DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    m4a_file = data_dir.joinpath(f'{movie_id}.m4a')

    url_reconstructed = f'https://youtu.be/{movie_id}'

    context['log'] = data_dir.joinpath(f'{movie_id}.log')
    if not m4a_file.exists():
        command = f'yt-dlp {config.YT_DLP_OPTIONS_DEFAULT} --output {m4a_file.as_posix()} {url_reconstructed}'
        print('❤️ BASH: ', command)

        process = subprocess.Popen(
            command.split(' '),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True)

        log_rows = []
        for line in process.stdout:
            line = line.strip()
            line = line.replace('https://youtu.be/', '').replace('https://www.youtube.com/', '')
            log_rows.append(line)

        with context['log'].open(mode='w') as f:
            f.write('\n'.join(log_rows))

    if not m4a_file.exists():
        context['error'] = f'🟥 Unexpected error in yt-dlp. [not m4a_file.exists()].'
        return context

    try:
        audio = MP4(m4a_file.as_posix())
    except Exception as e:
        context['error'] = f'🟥 Exception as e: [audio = MP4(m4a_file.as_posix())].'
        return context

    if not audio:
        context['error'] = '🟥 Unexpected error. [not audio in MP4 metadata].'
        return context

    title_orig = str(movie_id)
    if audio.get('\xa9nam'):
        title_orig = audio.get('\xa9nam')[0]

    duration_seconds = None
    if audio.info.length:
        duration_seconds = int(audio.info.length)

    context['thumbnail'] = data_dir.joinpath(f'{movie_id}.jpg')
    if not context['thumbnail'].exists():
        download_thumbnail(url_reconstructed, context['thumbnail'].as_posix())

    if not context['thumbnail'].exists():
        context['error'] = f'🟥 One problem. [not thumbnail.exists()]. Continue'
        return context

    if duration_seconds > config.SPLIT_THRESHOLD_MINUTES * 60:
        opt_split_minutes = config.SPLIT_AUDIO_DURATION_MINUTES

    filename = output_filename_in_telegram(title_orig)

    context['audios'] = [{
        'path': m4a_file.as_posix(),
        'duration': duration_seconds,
        'caption': title_orig,
        'filename': filename,
    }]

    if opt_split_minutes:
        # todo
        print('⌛ Splitting ... ')

        m4a_parts = make_split(m4a_file, duration_seconds, opt_split_minutes, config.SPLIT_DELTA_SECONDS)
        print('m4a_parts: ', m4a_parts)
        if m4a_parts:
            cmds_list = []
            for idx, part in enumerate(m4a_parts, start=1):
                output_file = m4a_file.with_stem(f'{m4a_file.stem}-p{idx}-of{len(m4a_parts)}')
                filename_local = f'(p{idx}-of{len(m4a_parts)}) {filename}'
                caption_local = f'[Part {idx} of {len(m4a_parts)}] {title_orig}'
                title = f''
                context['audios'].append({'file': output_file.as_posix(), 'duration': part[1] - part[0]})
                cmd = f'ffmpeg -i {m4a_file.as_posix()} -ss {time_format(part[0])} -to {time_format(part[1])} -c copy -y {output_file.as_posix()}'
                print(cmd)
                cmds_list.append(cmd.split(' '))

            processes = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for cmd in cmds_list]

            for idx, process in enumerate(processes):
                print('🔹 Process, ', idx)
                process.wait()

            print("🟢 All Done! Lets see .m4a files and their length")
            for m4a_obj in context['audios']:
                if not (file := m4a_obj.get('file')):
                    context['error'] = '🟥 Error. [not (file := m4a_obj.get]'
                    return context

                print(f'🔹 {file.name}')
                if not file.exists():
                    context['error'] = f'🟥 {file.name} This File Unexpected exists!'
                    return context

        if False:
            # todo
            if len(data.get('audios')) > 1:
                filename = f'(p{idx}-of{len(m4a_objs)}) {filename}'
                caption = f'[Part {idx} of {len(m4a_objs)}] {title}'

    context['thumbnail'] = context['thumbnail'].as_posix()
    context['log'] = context['log'].as_posix()

    print('🛵 CONTEXT: ', context)
    print()

    return context


