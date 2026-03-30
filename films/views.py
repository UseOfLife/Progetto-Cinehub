from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Avg
from .tmdb_service import get_popular_movies, get_movie_detail, get_movie_trailer, search_movies, build_poster_url
from .models import Review, Comment

def home(request):
	page = int(request.GET.get('page', 1))
	error = None
	movies = []
	try:
		data = get_popular_movies(page)
		print('TMDB POPULAR MOVIES RESPONSE:', data)
		movies = data['results']
		for m in movies:
			m['poster_url'] = build_poster_url(m.get('poster_path'))
			# Aggiungi media voti utenti (voto cinehub)
			avg_rating = Review.objects.filter(tmdb_id=m['id']).aggregate(avg=Avg('rating'))['avg']
			m['cinehub_rating'] = round(avg_rating, 1) if avg_rating else None
		paginator = Paginator(movies, len(movies) if movies else 1)
		page_obj = paginator.page(1)
	except Exception as e:
		error = str(e)
		print('TMDB ERROR:', error)
		page_obj = None
	return render(request, 'films/home.html', {'movies': movies, 'page_obj': page_obj, 'error': error})

def film_detail(request, tmdb_id):
	movie = get_movie_detail(tmdb_id)
	movie['poster_url'] = build_poster_url(movie.get('poster_path'))
	movie['backdrop_url'] = build_poster_url(movie.get('backdrop_path'))
	trailer_keys = get_movie_trailer(tmdb_id)
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
		'trailer_keys': trailer_keys,
		'comments': comments,
		'avg_rating': round(avg_rating, 1) if avg_rating else '-',
		'user_rating': user_rating,
	})

def search(request):
	query = request.GET.get('q', '')
	page = int(request.GET.get('page', 1))
	data = search_movies(query, page) if query else {'results': []}
	movies = data['results']
	for m in movies:
		m['poster_url'] = build_poster_url(m.get('poster_path'))
		# Aggiungi media voti utenti (voto cinehub)
		avg_rating = Review.objects.filter(tmdb_id=m['id']).aggregate(avg=Avg('rating'))['avg']
		m['cinehub_rating'] = round(avg_rating, 1) if avg_rating else None
	return render(request, 'films/search.html', {'movies': movies, 'query': query})

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
