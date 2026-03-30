from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Avg
from .tmdb_service import get_popular_movies, get_movie_detail, get_movie_trailer, search_movies, build_poster_url, get_movies_by_genre
from .models import Review, Comment

def home(request):
	page = int(request.GET.get('page', 1))
	error = None
	movies = []
	total_pages = 1
	try:
		data = get_popular_movies(page)
		print('TMDB POPULAR MOVIES RESPONSE:', data)
		movies = data['results']
		total_pages = data.get('total_pages', 1)
		for m in movies:
			m['poster_url'] = build_poster_url(m.get('poster_path'))
			# Aggiungi media voti utenti (voto cinehub)
			avg_rating = Review.objects.filter(tmdb_id=m['id']).aggregate(avg=Avg('rating'))['avg']
			m['cinehub_rating'] = round(avg_rating, 1) if avg_rating else None
		# Crea paginazione smart con massimo 5 tasti visibili
		page_range = []
		start_page = max(1, page - 2)
		end_page = min(total_pages, start_page + 4)
		
		# Se siamo vicino alla fine, sposta l'inizio
		if end_page - start_page < 4:
			start_page = max(1, end_page - 4)
		
		for i in range(start_page, end_page + 1):
			page_range.append(i)
		
		page_obj = type('PageObj', (), {
			'number': page,
			'has_previous': page > 1,
			'has_next': page < total_pages,
			'previous_page_number': page - 1 if page > 1 else None,
			'next_page_number': page + 1 if page < total_pages else None,
			'paginator': type('Paginator', (), {
				'num_pages': total_pages,
				'count': data.get('total_results', len(movies)),
				'page_range': page_range
			})()
		})()
	except Exception as e:
		error = str(e)
		print('TMDB ERROR:', error)
		page_obj = None
	return render(request, 'films/home.html', {'movies': movies, 'page_obj': page_obj, 'error': error})

def film_detail(request, tmdb_id):
	movie = get_movie_detail(tmdb_id)
	movie['poster_url'] = build_poster_url(movie.get('poster_path'))
	movie['backdrop_url'] = build_poster_url(movie.get('backdrop_path'))
	trailer_key = get_movie_trailer(tmdb_id)
	comments = Comment.objects.filter(tmdb_id=tmdb_id)
	avg_rating = Review.objects.filter(tmdb_id=tmdb_id).aggregate(avg=Avg('rating'))['avg']
	user_rating = None
	if request.user.is_authenticated:
		try:
			user_rating = Review.objects.get(tmdb_id=tmdb_id, user=request.user).rating
		except Review.DoesNotExist:
			user_rating = 0
	return render(request, 'films/detail.html', {
		'movie': movie,
		'trailer_key': trailer_key,
		'comments': comments,
		'avg_rating': round(avg_rating, 1) if avg_rating else '-',
		'user_rating': user_rating,
	})

def search(request):
	query = request.GET.get('q', '')
	page = int(request.GET.get('page', 1))
	data = search_movies(query, page) if query else {'results': [], 'total_pages': 1, 'total_results': 0}
	movies = data['results']
	total_pages = data.get('total_pages', 1)
	for m in movies:
		m['poster_url'] = build_poster_url(m.get('poster_path'))
		# Aggiungi media voti utenti (voto cinehub)
		avg_rating = Review.objects.filter(tmdb_id=m['id']).aggregate(avg=Avg('rating'))['avg']
		m['cinehub_rating'] = round(avg_rating, 1) if avg_rating else None
	
	# Crea paginazione smart con massimo 5 tasti visibili
		page_range = []
		start_page = max(1, page - 2)
		end_page = min(total_pages, start_page + 4)
		
		# Se siamo vicino alla fine, sposta l'inizio
		if end_page - start_page < 4:
			start_page = max(1, end_page - 4)
		
		for i in range(start_page, end_page + 1):
			page_range.append(i)
		
		page_obj = type('PageObj', (), {
			'number': page,
			'has_previous': page > 1,
			'has_next': page < total_pages,
			'previous_page_number': page - 1 if page > 1 else None,
			'next_page_number': page + 1 if page < total_pages else None,
			'paginator': type('Paginator', (), {
				'num_pages': total_pages,
				'count': data.get('total_results', len(movies)),
				'page_range': page_range
			})()
		})()
	
	return render(request, 'films/search.html', {'movies': movies, 'query': query, 'page_obj': page_obj})

def genre_view(request, genre_slug):
	# Mappa dei generi slug agli ID di TMDB
	genre_map = {
		'action': '28',
		'adventure': '12',
		'animation': '16',
		'comedy': '35',
		'crime': '80',
		'documentary': '99',
		'drama': '18',
		'family': '10751',
		'fantasy': '14',
		'history': '36',
		'horror': '27',
		'music': '10402',
		'mystery': '9648',
		'romance': '10749',
		'science-fiction': '878',
		'tv-movie': '10770',
		'thriller': '53',
		'war': '10752',
		'western': '37'
	}
	
	page = int(request.GET.get('page', 1))
	genre_id = genre_map.get(genre_slug, '28')  # Default a action se non trovato
	genre_name = genre_slug.replace('-', ' ').title()
	
	try:
		data = get_movies_by_genre(genre_id, page)
		movies = data['results']
		total_pages = data.get('total_pages', 1)
		
		for m in movies:
			m['poster_url'] = build_poster_url(m.get('poster_path'))
			# Aggiungi media voti utenti (voto cinehub)
			avg_rating = Review.objects.filter(tmdb_id=m['id']).aggregate(avg=Avg('rating'))['avg']
			m['cinehub_rating'] = round(avg_rating, 1) if avg_rating else None
		
		# Crea paginazione smart con massimo 5 tasti visibili
		page_range = []
		start_page = max(1, page - 2)
		end_page = min(total_pages, start_page + 4)
		
		# Se siamo vicino alla fine, sposta l'inizio
		if end_page - start_page < 4:
			start_page = max(1, end_page - 4)
		
		for i in range(start_page, end_page + 1):
			page_range.append(i)
		
		page_obj = type('PageObj', (), {
			'number': page,
			'has_previous': page > 1,
			'has_next': page < total_pages,
			'previous_page_number': page - 1 if page > 1 else None,
			'next_page_number': page + 1 if page < total_pages else None,
			'paginator': type('Paginator', (), {
				'num_pages': total_pages,
				'count': data.get('total_results', len(movies)),
				'page_range': page_range
			})()
		})()
		
	except Exception as e:
		movies = []
		page_obj = None
		error = str(e)
	
	return render(request, 'films/genre.html', {
		'movies': movies, 
		'genre_name': genre_name,
		'genre_slug': genre_slug,
		'page_obj': page_obj
	})

@login_required
@require_POST
def rate_film(request, tmdb_id):
	import json
	data = json.loads(request.body)
	rating = int(data.get('rating', 0))
	obj, _ = Review.objects.update_or_create(
		tmdb_id=tmdb_id, user=request.user,
		defaults={'rating': rating}
	)
	avg = Review.objects.filter(tmdb_id=tmdb_id).aggregate(avg=Avg('rating'))['avg']
	return JsonResponse({'ok': True, 'avg': round(avg, 1) if avg else '-'})

@login_required
@require_POST
def add_comment(request, tmdb_id):
	import json
	data = json.loads(request.body)
	text = data.get('text', '').strip()
	if not text:
		return JsonResponse({'ok': False}, status=400)
	comment = Comment.objects.create(tmdb_id=tmdb_id, user=request.user, text=text)
	return JsonResponse({
		'ok': True,
		'user': comment.user.username,
		'text': comment.text,
		'date': comment.created_at.strftime('%d/%m/%Y %H:%M'),
	})
