from django.contrib import admin
from .models import Game, Genre, Company, Collection, comments, reviews,Profile,Game_List

# Register your models here.

admin.site.register(Game)
admin.site.register(Genre)
admin.site.register(Company)
admin.site.register(Collection)
admin.site.register(comments)
admin.site.register(reviews)
admin.site.register(Profile)
admin.site.register(Game_List)