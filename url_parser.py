from urllib.parse import urlparse, parse_qs


def parse_input(input_text: str) -> (str, str):
    input_parts = input_text.split(' ')
    url = input_parts[0]
    discovered_word = ''
    if len(input_parts) > 1:
        discovered_word = input_parts[1]

    return url, discovered_word


def get_youtube_id(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Handle different YouTube URL formats
    if parsed_url.hostname in ('youtu.be'):
        return parsed_url.path[1:]

    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/live/'):
            return parsed_url.path.split('/')[2]

    return None