# Import necessary libraries
import datetime
import requests
import json
import boto3
import os
import logging
import time
import after_response
import re
from django.shortcuts import render, redirect
from django.db import models
from django.db.models import IntegerField, Q
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.views import generic
from catalog.models import *
from botocore.exceptions import ClientError
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import update_session_auth_hash
from catalog.forms import (
    gameSearch,
    RegisterForm,
    CommentBox,
    ReviewBox,
    NewList,
    existingLists,
    ProfileUploader,
    removeFromLists,
    updateForm,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.contrib.postgres.fields import ArrayField
from django.core.paginator import Paginator
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

load_dotenv()
# Create an S3 client
s3 = boto3.client("s3")

client_key=os.getenv('CLIENT_KEY')
client_secret=os.getenv('CLIENT_SECRET')

# Make a POST request to get an access token from Twitch API
x = requests.post(
    "https://id.twitch.tv/oauth2/token?client_id=" + client_key +"&client_secret=" + client_secret + "&grant_type=client_credentials"
)
test = x.json()
access_token = test["access_token"]
header = {
    "Client-ID": client_key,
    "Authorization": "Bearer " + access_token,
}




def game_add(new_game):
    # Create a new Game entry
    game_entry = Game()
    # Set the attributes of the game_entry object based on the value from the initial API response
    game_entry.id = new_game["id"]
    game_entry.game_title = new_game["name"]

    # Set the release_time attribute if first_release_date exists in the API response
    if new_game.get("first_release_date") is not None:
        game_entry.release_time = datetime.datetime.fromtimestamp(
            new_game["first_release_date"], tz=timezone.utc
        )

    # If cover image exists in the API response, call the add_image function after the response in order to reduce initial page load
    if new_game.get("cover") is not None:
        game_url_initial = "https:"
        add_image.after_response(game_url_initial, new_game, game_entry)

    # Set child_version attribute if version_parent exists in the API response
    if new_game.get("version_parent") is not None:
        game_entry.child_version = new_game["version_parent"]
    # Set child_edition attribute if parent_game exists in the API response
    elif new_game.get("parent_game") is not None:
        game_entry.child_edition = new_game["parent_game"]
        game_entry.save()

    # Set the summary attribute if summary exists in the API response
    if new_game.get("summary") is not None:
        game_entry.summary = new_game["summary"]

    # Initialize genre_list and company_list attributes
    game_entry.genre_list = []
    game_entry.company_list = []

    # Check if genres exist in the API response
    if new_game.get("genres") is not None:
        for each_genre in new_game["genres"]:
            # Add each genre to the genre_list attribute of the new game entry
            game_entry.genre_list.append(each_genre)

            # Check if the genre with the given genre_id exists in the Genre model
            genre_check = Genre.objects.filter(genre_id=each_genre)
            if not genre_check:
                # If the genre doesn't exist, make a request to retrieve its details from the API
                genre_url = "https://api.igdb.com/v4/genres"
                payload = "fields *; where id = {genre_id};".format(genre_id=each_genre)
                y = requests.post(
                    "https://api.igdb.com/v4/genres", headers=header, data=payload
                )
                genre_results = y.json()

                for genres in genre_results:
                    # Create a new Genre entry and set its attributes
                    new_genre = Genre()
                    new_genre.genre_id = genres["id"]
                    new_genre.genre_name = genres["name"]
                    new_genre.save()
            else:
                # The genre exists in the database, retrieve the Genre object
                genre_test = Genre.objects.filter(genre_id=each_genre)

    # Check if involved_companies exist in the API response
    if new_game.get("involved_companies") is not None:
        for each_company in new_game["involved_companies"]:
            # Set developer_id if developer is True
            if each_company["developer"]:
                game_entry.developer_id = each_company["company"]
            # Set publisher_id if publisher is True
            if each_company["publisher"]:
                game_entry.publisher_id = each_company["company"]

    # Save the game_entry object
    game_entry.save()

def game_description_view(request, pk):
    try:
        # Attempt to retrieve the game with the given primary key
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist:
        # If the game doesn't exist, raise an Http404 error
        raise Http404
        
    # Retrieve the publisher and developer companies associated with the game
    publisher = Company.objects.filter(company_id=game.publisher_id)
    developer = Company.objects.filter(company_id=game.developer_id)
    company_addition(developer, publisher, game)

    # Retrieve alternative editions and versions of the game
    alt_edition = Game.objects.filter(child_edition=pk)
    alt_version = Game.objects.filter(child_version=pk)

    game_genres = []
    for games in game.genre_list:
        # Retrieve the genres associated with the game
        game_genres.append(Genre.objects.filter(genre_id=games))

    # If the game doesn't have a large cover image, wait for 0.5 seconds and retrieve the game again
    while not game.cover_large_resized:
        time.sleep(0.5)
        game = Game.objects.get(pk=pk)

    # Retrieve reviews and comments associated with the game
    reviews_exist = reviews.objects.filter(game_id=game.id)
    comments_exist = comments.objects.filter(game_id=game.id)
    # Retrieve game lists that contain the current game
    containing_lists = Game_List.objects.filter(game_list__contains=[game.id]).order_by("?")[:6]
    publisher = Company.objects.filter(company_id=game.publisher_id)
    developer = Company.objects.filter(company_id=game.developer_id)



def search_results(request):
    # Get the value of the 'search_term' parameter from the request's GET data
    query = request.GET.get("search_term")

    # Send a request to an API to search for games using the query term
    y = requests.post(
        "https://api.igdb.com/v4/games?fields=*,cover.*,involved_companies.*&search="
        + query
        + "&limit=30",
        headers=header,
    )

    # Convert the response to JSON format
    testimage = y.json()

    # Create an empty list for storing search results
    search_results = []

    # Iterate over each item in testimage
    for each in testimage:
        # Append each item to the search_results list
        search_results.append(each)

        try:
            # Try to retrieve a Game object with the corresponding id from the database
            Game.objects.get(id=each["id"])
        except Game.DoesNotExist:
            # If the Game object does not exist, call the game_add function to add it
            game_add(each)

    # Create a Paginator object with search_results list and a limit of 15 items per page
    paginator = Paginator(search_results, 15)

    # Get the page number from the request's GET data
    page_number = request.GET.get("page")

    # Get the corresponding page object from the Paginator
    page_obj = paginator.get_page(page_number)
    context = {"tests": search_results, "page_obj": page_obj}
    # Render the 'catalog/search_results.html' template with the given context
    return render(request, "catalog/search_results.html", context=context)

def register(response):
    if response.method == "POST":
        # If the form is submitted via POST
        registration_form = RegisterForm(response.POST)
        if registration_form.is_valid():
            # If the form data is valid, save the user
            registration_form.save()
            # Create a new Profile for the newly created user
            new_profile = Profile()
            new_profile.user = registration_form.save()
            new_profile.save()
            # Redirect the user to the homepage
            return redirect("/")
    else:
        # If the form is not submitted via POST, create a new form instance
        registration_form = RegisterForm()

    # Render the register.html template with the form
    return render(response, "registration/register.html", {"form": registration_form})

def index(request):
    # Define the URL for the API endpoint to retrieve releases
    releases_url = "https://api.igdb.com/v4/multiquery"

    # Get the current date and time
    current_date = datetime.datetime.now()

    # Calculate the target dates for future and past releases
    target_date_future = int((current_date + datetime.timedelta(days=30)).timestamp())
    target_date_past = int((current_date - datetime.timedelta(days=14)).timestamp())

    # Define a time delta of 2 days
    d = datetime.timedelta(days=2)

    # Define the payload for the API request to retrieve upcoming and recent releases
    payload = (
        'query games "Upcoming Releases" {\r\nfields *,cover.*,involved_companies.*;\r\nwhere themes != (42) & first_release_date >= '
        + str(int(current_date.timestamp()))
        + " & first_release_date < "
        + str(target_date_future)
        + ';\r\nlimit 15;sort first_release_date desc;\r\n};\r\n\r\nquery games "Recent Releases" {\r\nfields *,cover.*,involved_companies.*;\r\nwhere themes != (42) & first_release_date >= '
        + str(target_date_past)
        + " & first_release_date < "
        + str(int(current_date.timestamp()))
        + ";\r\nlimit 15;sort first_release_date asc;\r\n};\r\n"
    )

    # Make a POST request to the releases URL with the payload and headers
    response = requests.request("POST", releases_url, headers=header, data=payload)
    release_response = response.json()

    # Iterate over the new games in the upcoming releases
    for new_games in release_response[0]["result"]:
        try:
            # Check if the game with the given id already exists in the Game model
            Game.objects.get(id=new_games["id"])
        except Game.DoesNotExist:
            # If the game doesn't exist, call the game_add function to add it
            game_add(new_games)

    # Iterate over the new games in the recent releases
    for new_games in release_response[1]["result"]:
        try:
            # Check if the game with the given id already exists in the Game model
            Game.objects.get(id=new_games["id"])
        except Game.DoesNotExist:
            # If the game doesn't exist, call the game_add function to add it
            game_add(new_games)

    # Retrieve all recent lists from the Game_List model
    all_recent_lists = (
        Game_List.objects.filter(published=True)
        .exclude(game_list__exact=[])
        .order_by("-creation_date")[:8]
    )

    # Retrieve all recent reviews from the reviews model
    all_recent_reviews = reviews.objects.filter().order_by("-post_date")[:6]

    # Retrieve upcoming releases within the next 30 days from the Game model
    upcoming_releases = Game.objects.filter(
        release_time__range=(current_date, current_date + datetime.timedelta(days=30))
    ).exclude(cover_large_resized__exact="")

    # Retrieve recent releases from the Game model within the past 14 days
    recent_releases = Game.objects.filter(
        release_time__range=(current_date - datetime.timedelta(days=14), current_date)
    ).exclude(cover_large_resized__exact="")

    # Retrieve all company objects from the Company model
    company_list = Company.objects.all()

    # Retrieve random genres from the Genre model
    random_genres = Genre.objects.filter().order_by("?")[:10]

    # Check if the user is authenticated and has a Profile object
    if request.user.is_authenticated and Profile.objects.get(user=request.user):
        # Retrieve the Profile object for the authenticated user
        profile = Profile.objects.get(user=request.user)

        # Initialize a game_list
        game_list = []

        # Check if the recently_viewed attribute in the profile is not None
        if profile.recently_viewed is not None:
            # Iterate over the recently viewed games and add them to the game_list
            for games in profile.recently_viewed:
                game_list.append(Game.objects.get(id=games))

        return render(
            request,
            "index.html",
            context={
                "recent_releases": recent_releases,
                "all_recent_lists": all_recent_lists,
                "all_recent_reviews": all_recent_reviews,
                "random_genres": random_genres,
                "upcoming_releases": upcoming_releases,
                "profile": profile,
                "game_list": game_list,
            },
        )
    else:
        return render(
            request,
            "index.html",
            context={
                "recent_releases": recent_releases,
                "all_recent_lists": all_recent_lists,
                "all_recent_reviews": all_recent_reviews,
                "random_genres": random_genres,
                "upcoming_releases": upcoming_releases,
                "company_list": company_list,
            },
        )
