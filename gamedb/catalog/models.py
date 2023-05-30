from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from tinymce.models import HTMLField 
from gamedb.storage import PublicMediaStorage
from django_resized import ResizedImageField

class Game(models.Model):
    # Represents a game
    game_title = models.CharField(max_length=200)  # Title of the game
    summary = models.TextField(max_length=2000)  # Summary of the game
    genre_list = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)  # List of genre IDs associated with the game
    developer_id = models.IntegerField(null=True, blank=True)  # ID of the game's developer
    publisher_id = models.IntegerField(null=True, blank=True)  # ID of the game's publisher
    id = models.IntegerField(unique=True, primary_key=True)  # Unique ID of the game
    child_edition = models.IntegerField(null=True, blank=True)  # Child edition of the game
    child_version = models.IntegerField(null=True, blank=True)  # Child version of the game
    release_time = models.DateTimeField(null=True, blank=True)  # Release time of the game
    overall_rating = models.IntegerField(null=True, blank=True, default=0)  # Total rating given to the game via reviews
    number_of_votes = models.IntegerField(null=True, blank=True, default=0)  # Total number of votes left
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, default=0)  # Average rating given to the game via reviews
    cover_large_resized = ResizedImageField(size=[400, 500],quality=90, upload_to='media/', blank=True, null=True)
    cover_thumb_resized = ResizedImageField(size=[150, 150],quality=90, upload_to='media/', blank=True, null=True)
    cover_mobile_resized =  ResizedImageField(size=[150, 200],quality=90, upload_to='media/', blank=True, null=True)


    def get_absolute_url(self):
        return reverse('game-description', args=[str(self.id)])
