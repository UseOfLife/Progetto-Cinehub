from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('film/<int:tmdb_id>/', views.film_detail, name='film_detail'),
    path('film/<int:tmdb_id>/rate/', views.rate_film, name='rate_film'),
    path('film/<int:tmdb_id>/comment/', views.add_comment, name='add_comment'),
]
