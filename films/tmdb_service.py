import requests
from django.conf import settings

BASE_URL = 'https://api.themoviedb.org/3'


def _get(endpoint, params=None):
    if params is None:
        params = {}
    params['api_key'] = settings.TMDB_API_KEY
    params['language'] = 'it-IT'
    url = f"{BASE_URL}{endpoint}"
    
    headers = {
        'Authorization': f'Bearer {getattr(settings, "TMDB_READ_ACCESS_TOKEN", "")}',
        'Content-Type': 'application/json;charset=utf-8'
    }
    
    print('TMDB REQUEST:', url, params)
    resp = requests.get(url, params=params, headers=headers)
    print('TMDB STATUS:', resp.status_code)
    print('TMDB RESPONSE:', resp.text[:500])
    resp.raise_for_status()
    return resp.json()


def get_popular_movies(page=1):
    return _get('/movie/popular', {'page': page, 'results_per_page': 10})


def get_movie_detail(tmdb_id):
    return _get(f'/movie/{tmdb_id}', {'append_to_response': 'credits'})


def get_movie_trailer(tmdb_id):
    data = _get(f'/movie/{tmdb_id}/videos')
    trailer_key = None
    for video in data.get('results', []):
        if video['site'] == 'YouTube' and video['type'] == 'Trailer' and video['official']:
            trailer_key = video['key']
            break
    
    if not trailer_key:
        for video in data.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                trailer_key = video['key']
                break
    
    if not trailer_key:
        for video in data.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Teaser':
                trailer_key = video['key']
                break
    
    return trailer_key if trailer_key else None


def search_movies(query, page=1):
    return _get('/search/movie', {'query': query, 'page': page, 'results_per_page': 10})


def get_movies_by_genre(genre_id, page=1):
    return _get('/discover/movie', {'with_genres': genre_id, 'page': page, 'results_per_page': 10})


def build_poster_url(path):
    if path:
        return f'https://image.tmdb.org/t/p/w500{path}'
    return '/static/css/no-poster.jpg'
