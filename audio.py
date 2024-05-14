import subprocess

from mutagen.wave import WAVE
from mutagen.ogg import OggFileType
from mutagen.mp4 import MP4
import math
import pathlib
import config


def get_song_duration(fullpath: pathlib.Path):
    if fullpath.suffix in config.SONG_SUPPORTED_EXTENSIONS:
        if fullpath.suffix in ['.wav']:
            return math.ceil(WAVE(fullpath.as_posix()).info.length)

        if fullpath.suffix in ['.ogg']:
            return math.ceil(OggFileType(fullpath.as_posix()).info.length)

        if fullpath.suffix in ['.m4a']:
            return math.ceil(MP4(fullpath.as_posix()).info.length)

    else:
        print('🚫 Not supported song format')
        return
