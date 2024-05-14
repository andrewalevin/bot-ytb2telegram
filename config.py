import pathlib
from string import Template

VOICES_AVAILABLE = {
    '0': {
        'name': '',
        'role': ''
    },
    '21': {
        'name': 'alena',
        'role': 'good'
    },
    '22': {
        'name': 'ermil',
        'role': 'good'
    },
    '23': {
        'name': 'jane',
        'role': 'good'
    },
    '24': {
        'name': 'zahar',
        'role': 'good'
    },
    '25': {
        'name': 'dasha',
        'role': 'good'
    },
    '26': {
        'name': 'dasha',
        'role': 'friendly'
    },
    '27': {
        'name': 'lera',
        'role': 'friendly'
    },
    '28': {
        'name': 'masha',
        'role': 'good'
    },
    '29': {
        'name': 'masha',
        'role': 'friendly'
    },
    '30': {
        'name': 'marina',
        'role': 'friendly'
    },
    '31': {
        'name': 'alexander',
        'role': 'good'
    },
    '32': {
        'name': 'kirill',
        'role': 'good'
    },
    '33': {
        'name': 'anton',
        'role': 'good'
    }
}

VOICES_All = '''
alena-neutral
alena-good
filipp-
ermil-neutral
ermil-good
jane-neutral
jane-neutral
jane-good
madirus-
omazh-neutral
omazh-evil
zahar-neutral
zahar-good
dasha-neutral
dasha-good
dasha-friendly
julia-neutral
julia-strict
lera-neutral
lera-friendly
masha-good
masha-strict
masha-friendly
marina-neutral
marina-whisper
marina-friendly
alexander-neutral
alexander-good
kirill-neutral
kirill-strict
kirill-good
anton-neutral
anton-good
'''

STORE_DIR = pathlib.Path('store')

USER_DIR_STORE_TEMPLATE = Template('user-$user_id')

POST_FILENAME_TEMPLATE = Template('post-$id.yaml')

LOGBOOK_RECORD_TEMPLATE = Template('$postid-$voiceid-$timestamp-$probability')

LOGBOOK_FILENAME = 'logbook.log'


MAX_TEXT_LENGTH = 64

PAUSE_PODCAST_DURATION = 3
PAUSE_PODCAST_FILENAME = ''

BOT_TOKEN = 'AQVN2svr7LDcufQimEZxt1h50mWv10bEIGLqmMeC'


SONG_PAUSE_ONE_SECOND_PATH = pathlib.Path('static/void/void-1-sec.wav')

PAUSE_SONGS = {
    '1': pathlib.Path('static/void/void-1-sec.wav'),
    '2': pathlib.Path('static/void/void-2-sec.wav'),
    '3': pathlib.Path('static/void/void-3-sec.wav'),
    '5': pathlib.Path('static/void/void-5-sec.wav'),
    '7': pathlib.Path('static/void/void-7-sec.wav')
}

PODCAST_FILENAME_TEMPLATE = Template('podcast-$id.wav')

PODCAST_MAX_DURATION = 30


SONG_SUPPORTED_EXTENSIONS = [
    '.wav',
    '.ogg',
    '.m4a',
]

DEFAULT_VOICE_NAME = 'alexander'
DEFAULT_VOICE_ROLE = 'good'


YAML_EXTS = [
    '.yml',
    '.yaml'
]


SONG_FILENAME_TEMPLATE = Template(f'song-$id-voice-$voiceid$ext')

SONG_ANNOTATION_FILENAME_TEMPLATE = Template(f'song-$id-voice-$voiceid-annotation$ext')

SONG_ANNOTATION_TEXT = Template(f'Пост № $postid, $voiceid. ')

SONG_PODCAST_ITEM_VOICEOVER_FILENAME_TEMPLATE = Template(f'song-podcast-$podcastid$ext')

SONG_DEMO_FILE = pathlib.Path('static/demo-song.wav')

SONG_CURRENT_FORMAT = '.wav'


TIMERS_MAX_NUMBER = 5

TIMERS_MIN_TIME = 0
TIMERS_MAX_TIME = 23

PAUSE_MIN_SECONDS = 1
PAUSE_MAX_SECONDS = 60


PODCASTS_DIR = pathlib.Path('podcasts')
SONGS_DIR = pathlib.Path('songs')
POSTS_DIR = pathlib.Path('posts')

HELP_TEXT = '''
<b>👋 Hello!</b>
This Bot lets you .. .

🚩Supported language: RU only 
(other will be available later)

<b>🔮 Usage:</b>

<b> - 🔄 Update text.</b>
Edit your target post and save it in telegram. It will automatically updated.


<b> - 🗑 Delete posts from stack.</b>
Edit target post and add Del or del word below text'
<pre language="text">
del Post text ...
</pre>
or 
<pre language="text">
Del Post text ...
</pre>

etc.

'''

CODE_IVITE = 'pwp-code-d807c12'

CODE_FOR_FRIENDS_TEXT = f'''
<b>🧞‍ Code for friends </b>

Copy text below and paste it in your bot

<a href="@dev_privata_fluctus_bot">@dev_privata_fluctus_bot</a>

<pre language="text">
/code {CODE_IVITE}
</pre>

'''

PODCAST_INSIDE_VOICE_TEXT = Template('Подкаст №$id ')

PODCAST_TITLE_TEXT = Template(f'$emoji Podcast № $id ')

EMOJI = '''
🦆🦅🦉🦇🦄🐝🪱🐛🦋🐞🪲🦂🐢🐍🦎🦖🦕🦐🦞🦀🐠🐬🐳🐊🐅🐆🦓🦧🦣🐘
🦛🦏🐪🐫🦒🦘🦬🐃🐂🐎🐐🦌🐕‍🐈🦤🦚🦜🦩🦫🐿🦔🐉🐲🌲🌳🌴🌿🪴🍁🪷
🌖🌗🌘🌑🌒🌓🌔🌎🌍🌏🪐💥🔥🍏🍎🍐🍊🍋🍉🍇🍓🫐🍈🍒🍑🥭🍍🥥🥝🍅
🥑🌶🌽🥕🥐🍕🥗🍱🍨🍦🧁🍰🍭🍫🍹🏎🚲🛵🚂🛫🚀🛸🚁🛶🚢🗽🏰🎠🏖🏝
🏜🌋🏔🗻🏕🏛🏞🌅🌄🌠🎇🎆🌇🌆🌃🌌🌉
'''

PREFERENCES_DEFAULT_DATA = {
    'pause': 2,
    'timers': [],
    'voices': ['21', '25', '26', '27', '28', '29', '30', '31', '32', '33'],
    'podcast_show_voices': False,
    'podcast_show_posts': False,
}

PREFERENCES_FILENAME = 'preferences.yml'

AUTO_START_OVER_TIMEOUT = 2


PAUSES_ALL = [0, 1, 2, 3, 4, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]

CONVERSATION_MAIN_START_TEXT = '''
<b>🥗🍒 Private Wave Podcast BAR 🥦🍍</b>

🥒 You can cook your private podcast

🕰 Add timer to get auto daily new podcast

🍱 Change multiple Preferences to shake the best

🍹 and enjoy
'''


CONVERSATION_HELP_TEXT = f'''
<b>🥗🍒 To start Private Wave Podcast BAR 🥦🍍</b>
send me a command

<a href="@privata_fluctus_bot">/start</a>

'''


PREFERENCES_VIEW_TEMPLATE = Template('''
<b>🍱 Preferences</b>

<b>🕰 Timers</b>
$timers_view

<b>🎷 Voices</b>
$voices_view

<b>⌛ Pause</b>
$pause_view

<b>🍱 Podcast Details</b>
$podcast_details

<b>🎞 Podcast Details Annotate</b>
$podcast_annotate_details
''')

PREFERENCES_ADDITIONAL_TEXT_TEMPLATE = Template('''
$text
================

$additional_text
''')


CHEAT_CODES = [
    '12',
    '128',
    '99999999',
]