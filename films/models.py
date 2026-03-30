from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
	tmdb_id = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	rating = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['tmdb_id', 'user'], name='unique_review')
		]

class Comment(models.Model):
	tmdb_id = models.IntegerField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.TextField(max_length=1000)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
