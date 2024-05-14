import socket

import config
import config_token


def get_running_mode():
    if config_token.DEVELOPMENT_HOSTNAME == socket.gethostname():
        print('🛵 Development Env: ')
        print()

        return 'development'

        settings = config_token.BOT_CONFIG['development']
        return settings['token'], settings['chat_id']

    else:
        print('🚠 Production Env: ')
        print()

        return 'production'

        settings = config_token.BOT_CONFIG['production']
        return settings['token'], settings['chat_id']
