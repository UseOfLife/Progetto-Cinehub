import requests
from django.conf import settings

BASE_URL = 'https://api.themoviedb.org/3'


def _get(endpoint, params=None):
    if params is None:
        params = {}
    params['api_key'] = settings.TMDB_API_KEY
    params['language'] = 'it-IT'
    url = f"{BASE_URL}{endpoint}"
    print('TMDB REQUEST:', url, params)
    resp = requests.get(url, params=params)
    print('TMDB STATUS:', resp.status_code)
    print('TMDB RESPONSE:', resp.text[:500])
    resp.raise_for_status()
    return resp.json()


def get_popular_movies(page=1):
    return _get('/movie/popular', {'page': page})


def get_movie_detail(tmdb_id):
    return _get(f'/movie/{tmdb_id}', {'append_to_response': 'credits'})


def get_movie_trailer(tmdb_id):
    data = _get(f'/movie/{tmdb_id}/videos')
    # Raccogli tutti i video YouTube disponibili (trailer, clip, featurette, ecc.)
    youtube_keys = []
    for video in data.get('results', []):
        if video['site'] == 'YouTube':
            youtube_keys.append(video['key'])
    return youtube_keys if youtube_keys else None


def search_movies(query, page=1):
    return _get('/search/movie', {'query': query, 'page': page})


def build_poster_url(path):
    if path:
        return f'https://image.tmdb.org/t/p/w500{path}'
    return '/static/css/no-poster.jpg'
