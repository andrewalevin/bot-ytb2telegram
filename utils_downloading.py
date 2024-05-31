#!/usr/bin/env python

import re
import ssl
from datetime import timedelta
import requests

from audio_parts import get_splitting_parts
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


def time_format(seconds):
    if not isinstance(seconds, int):
        print('🛑 time_format(): Variable is not int')
        return '00:00:00'
    if seconds < 0:
        print('🛑 time_format(): Variable is < 0 ')
        return '00:00:00'

    return '{:0>8}'.format(str(timedelta(seconds=int(seconds))))

