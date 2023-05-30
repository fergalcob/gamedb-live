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

client_key = os.getenv("CLIENT_KEY")
client_secret = os.getenv("CLIENT_SECRET")

# Make a POST request to get an access token from Twitch API
x = requests.post(
    "https://id.twitch.tv/oauth2/token?client_id="
    + client_key
    + "&client_secret="
    + client_secret
    + "&grant_type=client_credentials"
)
test = x.json()
access_token = test["access_token"]
header = {
    "Client-ID": client_key,
    "Authorization": "Bearer " + access_token,
}


@after_response.enable
def add_image(game_url_initial, api_response, db_entry):
    # Call the image_upload function with the necessary parameters
    image_upload(game_url_initial, api_response, db_entry)


@after_response.enable
def company_updater(id):
    company_query(id)


# Upload images to S3 and update the database entry
def image_upload(game_url_initial, api_response, db_entry):
    # Save the thumbnail and full-size cover image locally and
    # upload the thumbnail and full-size cover image to S3 bucket
    f = Image.open(
        requests.get(
            game_url_initial + api_response["cover"]["url"], stream=True
        ).raw
    )
    upload_file_stream = BytesIO()
    f.save(upload_file_stream, format="webp")
    upload_file_stream.seek(0)
    db_entry.cover_thumb_resized = ContentFile(
        upload_file_stream.getvalue(), "cover_thumb.webp"
    )
    f.close()

    f = Image.open(
        requests.get(
            game_url_initial
            + api_response["cover"]["url"].replace("t_thumb", "t_cover_big"),
            stream=True,
        ).raw
    )
    upload_file_stream = BytesIO()
    f.save(upload_file_stream, format="webp")
    upload_file_stream.seek(0)
    db_entry.cover_large_resized = ContentFile(
        upload_file_stream.getvalue(), "cover.webp"
    )
    db_entry.cover_mobile_resized = ContentFile(
        upload_file_stream.getvalue(), "cover_mobile.webp"
    )
    f.close()
    db_entry.save()


def averages(game_id, rating):
    review_update = Game.objects.get(id=game_id)
    review_update.overall_rating += rating
    review_update.number_of_votes += 1
    review_update.average_rating = (
        review_update.overall_rating / review_update.number_of_votes
    )
    review_update.save()


def company_query(company_identifier):
    # Retrieve the company from the initial request
    company_entry = Company.objects.get(company_id=company_identifier)
    # Create the payload for the API request with the company ID
    payload = "fields *; where id = {company_id};".format(
        company_id=company_entry.company_id
    )
    # Send a POST request to the IGDB API to get company information
    y = requests.post(
        "https://api.igdb.com/v4/companies", headers=header, data=payload
    )
    company_results = y.json()
    for companies in company_results:
        # Update the existing company object with the retrieved information
        company_update = Company.objects.get(company_id=companies["id"])
        try:
            # Update the list of developed games for the company
            for developed_games in companies["developed"]:
                if company_update.developed_list is None:
                    company_update.developed_list = []
                # Add the developed game to the list
                # if it's not already present
                if developed_games not in company_update.developed_list:
                    company_update.developed_list.append(developed_games)
                company_update.save()
        except KeyError:
            # Skip company if they have developed but not published games
            continue
        try:
            # Update the list of published games for the company
            for published_games in companies["published"]:
                if company_update.published_list is None:
                    company_update.published_list = []
                # Add the published game to the list
                # if it's not already present
                if published_games not in company_update.published_list:
                    company_update.published_list.append(published_games)
                company_update.save()
        except KeyError:
            # Skip company if they have published but not developed games
            continue
        company_confirmation()


def company_addition(developer, publisher, game):
    # If developer information is not available,
    # retrieve it from an external API
    if not developer:
        try:
            # Construct the payload for the API request
            payload = "fields *; where id = {company_id};".format(
                company_id=game.developer_id
            )
            y = requests.post(
                "https://api.igdb.com/v4/companies",
                headers=header,
                data=payload,
            )
            company_results = y.json()
            for companies in company_results:
                # Create a new Company instance and save it
                new_company = Company()
                new_company.company_id = companies["id"]
                new_company.company_name = companies["name"].title()
                new_company.developed_list = [game.id]
                new_company.save()
                developer = new_company
        except KeyError:
            print("no developer")
    else:
        if developer[0].developed_list is not None:
            developer[0].developed_list.append(game.id)
        else:
            developer[0].developed_list = [game.id]
        developer[0].save()

    # If publisher information is not available,
    # retrieve it from an external API
    if not publisher:
        try:
            # Construct the payload for the API request
            payload = "fields *; where id = {company_id};".format(
                company_id=game.publisher_id
            )
            y = requests.post(
                "https://api.igdb.com/v4/companies",
                headers=header,
                data=payload,
            )
            company_results = y.json()
            for companies in company_results:
                # Create a new Company instance and save it
                new_company = Company()
                new_company.company_id = companies["id"]
                new_company.company_name = companies["name"].title()
                new_company.published_list = [game.id]
                new_company.save()
                publisher = new_company
        except KeyError:
            print("no publisher")
    else:
        if publisher[0].published_list is not None:
            publisher[0].published_list.append(game.id)
        else:
            publisher[0].published_list = [game.id]
        publisher[0].save()
    return publisher, developer


def company_confirmation():
    # Retrieve a list of all companies
    companies_list = Company.objects.all()
    for each_company in companies_list:
        if each_company.published_list:
            # Retrieve the games published by the company
            published_games = Game.objects.filter(
                publisher_id=each_company.company_id
            )
            for each_game in published_games:
                # Add the game to the published list
                # of the company if it's not already present
                if each_game.id not in each_company.published_list:
                    each_company.published_list.append(each_game.id)
        if each_company.developed_list:
            # Retrieve the games developed by the company
            developed_games = Game.objects.filter(
                developer_id=each_company.company_id
            )
            for each_game in developed_games:
                # Add the game to the developed list
                # of the company if it's not already present
                if each_game.id not in each_company.developed_list:
                    each_company.developed_list.append(each_game.id)
        # Save the updated company object
        each_company.save()


def game_add(new_game):
    # Create a new Game entry
    game_entry = Game()
    # Set the attributes of the game_entry
    # object based on the value from the initial API response
    game_entry.id = new_game["id"]
    game_entry.game_title = new_game["name"]

    # Set the release_time attribute if
    # first_release_date exists in the API response
    if new_game.get("first_release_date") is not None:
        game_entry.release_time = datetime.datetime.fromtimestamp(
            new_game["first_release_date"], tz=timezone.utc
        )

    # If cover image exists in the API response, call the
    # add_image function after the response
    # in order to reduce initial page load
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

            # Check if the genre with the given
            # genre_id exists in the Genre model
            genre_check = Genre.objects.filter(genre_id=each_genre)
            if not genre_check:
                # If the genre doesn't exist,
                # make a request to retrieve its details from the API
                genre_url = "https://api.igdb.com/v4/genres"
                payload = "fields *; where id = {genre_id};".format(
                    genre_id=each_genre
                )
                y = requests.post(
                    "https://api.igdb.com/v4/genres",
                    headers=header,
                    data=payload,
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

    # If the game doesn't have a large cover image,
    # wait for 0.5 seconds and retrieve the game again
    while not game.cover_large_resized:
        time.sleep(0.5)
        game = Game.objects.get(pk=pk)

    # Retrieve reviews and comments associated with the game
    reviews_exist = reviews.objects.filter(game_id=game.id)
    comments_exist = comments.objects.filter(game_id=game.id)
    # Retrieve game lists that contain the current game
    containing_lists = Game_List.objects.filter(
        game_list__contains=[game.id]
    ).order_by("?")[:6]
    publisher = Company.objects.filter(company_id=game.publisher_id)
    developer = Company.objects.filter(company_id=game.developer_id)
    if request.user.is_authenticated:
        # Retrieve the user's profile
        user_profile = Profile.objects.get(user=request.user)

        if user_profile.recently_viewed is None:
            # If the recently viewed list is empty,
            # initialize it with the current game
            user_profile.recently_viewed = [game.id]
        elif (
            len(user_profile.recently_viewed) < 10
            and game.id not in user_profile.recently_viewed
        ):
            # If the recently viewed list is not full and
            # the game is not already in it, add the game to the list
            user_profile.recently_viewed.append(game.id)
        elif (
            len(user_profile.recently_viewed) == 10
            and game.id not in user_profile.recently_viewed
        ):
            # If the recently viewed list is full and the game
            # is not already in it, replace the
            # oldest game with the current game
            user_profile.recently_viewed.pop(0)
            user_profile.recently_viewed.append(game.id)

        user_profile.save()

        # Create instances for review and comment forms
        review = ReviewBox()
        comment = CommentBox()

        # Retrieve collections (game lists)owned by the user
        data = Collection.objects.filter(owner=request.user.id)
        # Initialize instances for adding and removing the game from game lists
        existing_lists = existingLists()
        remove_from_list = removeFromLists()
        remove_from_list.fields[
            "remove_from_list"
        ].queryset = Game_List.objects.filter(
            Q(creator=request.user.id) & Q(game_list__contains=[game.id])
        )
        if Game_List.objects.filter(
            Q(creator=request.user.id) & Q(game_list__contains=[game.id])
        ):
            # If the game is already in a game list created
            # by the user, retrieve other game lists excluding the current game
            existing_lists.fields[
                "add_to_list"
            ].queryset = Game_List.objects.filter(
                Q(creator=request.user.id)
            ).exclude(
                Q(game_list__contains=[game.id])
            )
        else:
            # If the game is not in any game list created
            # by the user, retrieve all game lists created by the user
            existing_lists.fields[
                "add_to_list"
            ].queryset = Game_List.objects.filter(Q(creator=request.user.id))

        in_collection = False
        if data is not None:
            for items in data:
                # Check if the game is already in the user's collection
                if game.id == items.game_name.id:
                    in_collection = True

        return render(
            request,
            "catalog/game_description.html",
            context={
                "game": game,
                "reviews": reviews_exist,
                "comments": comments_exist,
                "game_genres": game_genres,
                "publisher": publisher,
                "developer": developer,
                "in_collection": in_collection,
                "review": review,
                "comment": comment,
                "alt_version": alt_version,
                "alt_edition": alt_edition,
                "existing_lists": existing_lists,
                "remove_from_list": remove_from_list,
                "containing_lists": containing_lists,
            },
        )
    else:
        return render(
            request,
            "catalog/game_description.html",
            context={
                "game": game,
                "reviews": reviews_exist,
                "comments": comments_exist,
                "game_genres": game_genres,
                "publisher": publisher,
                "developer": developer,
                "alt_version": alt_version,
                "alt_edition": alt_edition,
                "containing_lists": containing_lists,
            },
        )


def submit_review(request, pk):
    if request.method == "POST" and request.user.is_authenticated:
        submit_review_form = ReviewBox(request.POST)
        if submit_review_form.is_valid():
            # Create a new review instance
            new_review = reviews()

            # Set the author of the review as the current user
            new_review.author = request.user

            # Set the review title from the 'title' field in the form data
            new_review.review_title = submit_review_form.cleaned_data["title"]

            # Set the review comment from the 'comment' field in the form data
            new_review.comment = submit_review_form.cleaned_data["comment"]

            # Set the game_id of the review by retrieving
            # the Game object with the given 'pk' value
            new_review.game_id = Game.objects.get(pk=pk)

            # Set the post date of the review as the current datetime
            new_review.post_date = datetime.datetime.now()

            # Set the rating of the review from
            # the 'Review' field in the form data
            new_review.rating = submit_review_form.cleaned_data["Review"]

            # Save the new review to the database
            new_review.save()
            averages(pk, new_review.rating)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            return redirect(reverse("game-description", args=[pk]))


def delete_review(request):
    review_deletion = reviews.objects.get(id=request.POST["review_id"])
    review_deletion.delete()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def edit_review(request):
    if request.method == "POST":
        reviewForm = ReviewBox(request.POST)
        if reviewForm.is_valid():
            review_editing = reviews.objects.get(id=request.POST["review_id"])
            review_editing.review_title = reviewForm.cleaned_data["title"]
            review_editing.comment = (
                reviewForm.cleaned_data["comment"]
                .replace("<p></p>", "")
                .replace("<p>&nbsp;</p>", "")
            )
            review_editing.comment = "\n".join(
                [line for line in review_editing.comment.splitlines() if line]
            )
            review_editing.rating = reviewForm.cleaned_data["Review"]
            review_editing.save()
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])


def submit_comment(request, pk):
    if request.method == "POST" and request.user.is_authenticated:
        submit_comment_form = CommentBox(request.POST)
        if submit_comment_form.is_valid():
            # Create a new comment instance
            new_comment = comments()

            # Set the author of the comment as the current user
            new_comment.author = request.user

            # Set the comment title from the 'title'
            # field in the request's POST data
            new_comment.comment_title = submit_comment_form.cleaned_data[
                "title"
            ]

            # Set the comment content from the 'comment'
            # field in the request's POST data
            new_comment.comment = submit_comment_form.cleaned_data["comment"]

            # Set the game_id of the comment by retrieving
            # the Game object with the given 'pk' value
            new_comment.game_id = Game.objects.get(pk=pk)

            # Set the post date of the comment as the current datetime
            new_comment.post_date = datetime.datetime.now()

            # Set is_reply attribute of the comment as True
            new_comment.is_reply = True

            # Set the parent_comment attribute of the comment
            # from the 'parent_comment' field in the request's POST data
            new_comment.parent_comment = request.POST.get("parent_comment")

            # Save the new comment to the database
            new_comment.save()

            # Retrieve the review associated with the parent comment
            # and set its has_reply attribute as True
            set_reply = reviews.objects.get(id=new_comment.parent_comment)
            set_reply.has_reply = True
            set_reply.save()

            # Redirect the user to the previous page
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            return redirect(reverse("game-description", args=[pk]))


def delete_reply(request):
    reply_deletion = comments.objects.get(id=request.POST["comment_id"])
    # Test for remaining comments
    other_comments = comments.objects.filter(
        parent_comment=reply_deletion.parent_comment
    ).exclude(id=reply_deletion.id)
    if not other_comments:
        set_parent = reviews.objects.get(id=reply_deletion.parent_comment)
        set_parent.has_reply = False
        set_parent.save()

    reply_deletion.delete()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def edit_reply(request):
    if request.method == "POST":
        reply_form = CommentBox(request.POST)
        if reply_form.is_valid():
            reply_editing = comments.objects.get(id=request.POST["comment_id"])
            reply_editing.comment_title = reply_form.cleaned_data["title"]
            reply_editing.comment = (
                reply_form.cleaned_data["comment"]
                .replace("<p></p>", "")
                .replace("<p>&nbsp;</p>", "")
            )
            reply_editing.comment = "\n".join(
                [line for line in reply_editing.comment.splitlines() if line]
            )
            reply_editing.save()
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])


def search_results(request):
    # Get the value of the 'search_term' parameter from the request's GET data
    query = request.GET.get("search_term")

    # Send a request to an API to search for games using the query term
    y = requests.post(
        "https://api.igdb.com/v4/games?fields=*,"
        "cover.*,involved_companies.*&search="
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
            # Try to retrieve a Game object with the
            # corresponding id from the database
            Game.objects.get(id=each["id"])
        except Game.DoesNotExist:
            # If the Game object does not exist,
            # call the game_add function to add it
            game_add(each)

    # Create a Paginator object with search_results
    # list and a limit of 15 items per page
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
    return render(
        response, "registration/register.html", {"form": registration_form}
    )


def index(request):
    # Define the URL for the API endpoint to retrieve releases
    releases_url = "https://api.igdb.com/v4/multiquery"

    # Get the current date and time
    current_date = datetime.datetime.now()

    # Calculate the target dates for future and past releases
    target_date_future = int(
        (current_date + datetime.timedelta(days=30)).timestamp()
    )
    target_date_past = int(
        (current_date - datetime.timedelta(days=14)).timestamp()
    )

    # Define a time delta of 2 days
    d = datetime.timedelta(days=2)

    # Define the payload for the API request
    # to retrieve upcoming and recent releases
    payload = (
        'query games "Upcoming Releases" {\r\nfields *,cover.*,'
        'involved_companies.*;\r\nwhere themes != (42)'
        '& first_release_date >= '
        + str(int(current_date.timestamp()))
        + " & first_release_date < "
        + str(target_date_future)
        + ';\r\nlimit 15;sort first_release_date desc;\r\n};\r\n\r\nquery'
        'games "Recent Releases" {\r\nfields *,cover.*,involved_companies.*;'
        '\r\nwhere themes != (42) & first_release_date >= '
        + str(target_date_past)
        + " & first_release_date < "
        + str(int(current_date.timestamp()))
        + ";\r\nlimit 15;sort first_release_date asc;\r\n};\r\n"
    )

    # Make a POST request to the releases URL with the payload and headers
    response = requests.request(
        "POST", releases_url, headers=header, data=payload
    )
    release_response = response.json()

    # Iterate over the new games in the upcoming releases
    for new_games in release_response[0]["result"]:
        try:
            # Check if the game with the given id
            # already exists in the Game model
            Game.objects.get(id=new_games["id"])
        except Game.DoesNotExist:
            # If the game doesn't exist, call the game_add function to add it
            game_add(new_games)

    # Iterate over the new games in the recent releases
    for new_games in release_response[1]["result"]:
        try:
            # Check if the game with the given id#
            # already exists in the Game model
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
        release_time__range=(
            current_date,
            current_date + datetime.timedelta(days=30),
        )
    ).exclude(cover_large_resized__exact="")

    # Retrieve recent releases from the Game model within the past 14 days
    recent_releases = Game.objects.filter(
        release_time__range=(
            current_date - datetime.timedelta(days=14),
            current_date,
        )
    ).exclude(cover_large_resized__exact="")

    # Retrieve all company objects from the Company model
    company_list = Company.objects.all()

    # Retrieve random genres from the Genre model
    random_genres = Genre.objects.filter().order_by("?")[:10]

    # Check if the user is authenticated and has a Profile object
    if request.user.is_authenticated and Profile.objects.get(
        user=request.user
    ):
        # Retrieve the Profile object for the authenticated user
        profile = Profile.objects.get(user=request.user)

        # Initialize a game_list
        game_list = []

        # Check if the recently_viewed attribute in the profile is not None
        if profile.recently_viewed is not None:
            # Iterate over the recently viewed games
            # and add them to the game_list
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


def account_profile(response):
    if response.user.is_authenticated:
        # Retrieve additional profile information for the current user
        additional_profile_information = Profile.objects.get(
            user=response.user
        )
        # Create a form instance for updating the password
        profile_update_form = ProfileUploader()
        # Render the profile.html template with the profile
        # information and form
        return render(
            response,
            "accounts/profile.html",
            context={
                "additional_profile_information":
                    additional_profile_information,
                "profile_uploader": profile_update_form,
            },
        )
    else:
        raise PermissionDenied()


def profile_picture(response):
    # Retrieve the profile object for the current user
    update_profile_picture = Profile.objects.get(user=response.user)
    # Update the profile picture with the uploaded file
    update_profile_picture.profile_picture = response.FILES["profile_pic"]
    # Save the updated profile
    update_profile_picture.save()
    return HttpResponseRedirect(response.META["HTTP_REFERER"])


def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Create a PasswordChangeForm instance with the
            # current user and submitted data
            password_change_form = PasswordChangeForm(
                request.user, request.POST
            )
            if password_change_form.is_valid():
                # Save the new password and update
                # the session authentication hash
                user = password_change_form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, "Your password was successfully updated!"
                )
                return redirect("change_password")
            else:
                messages.error(request, "Please correct the error below.")
        else:
            # Create a PasswordChangeForm instance with the current user
            password_change_form = PasswordChangeForm(request.user)
        return render(
            request,
            "accounts/change_password.html",
            {"form": password_change_form},
        )
    else:
        raise PermissionDenied


def update_profile(request):
    if request.user.is_authenticated:
        profile_update_form = updateForm()
        context = {"profile_update_form": profile_update_form}
        return render(request, "accounts/update_profile.html", context=context)
    else:
        raise PermissionDenied


def profile_changes(request):
    if request.method == "POST" and request.user.is_authenticated:
        update_form = updateForm(request.POST)
        if update_form.is_valid():
            profile_update = User.objects.get(id=request.user.id)
            profile_update.email = update_form.cleaned_data["email"]
            profile_update.first_name = update_form.cleaned_data["first_name"]
            profile_update.last_name = update_form.cleaned_data["last_name"]
            profile_update.save()
            return render(request, "accounts/profile.html", context=context)
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])


def reviews_and_comments(request):
    if request.user.is_authenticated:
        my_reviews = reviews.objects.filter(author=request.user)
        my_comments = comments.objects.filter(author=request.user)
        context = {"my_reviews": my_reviews, "my_comments": my_comments}
        return render(
            request, "accounts/reviews_comments.html", context=context
        )
    else:
        raise PermissionDenied


def my_collection(response):
    # Retrieve the collection data for the current user
    if response.user.is_authenticated:
        data = Collection.objects.filter(owner=response.user.id)
        context = {"personal_collection": data}
        return render(response, "accounts/collection.html", context=context)
    else:
        raise PermissionDenied()


def add_button(request):
    # Get the user and game IDs from the request
    user_id = User.objects.get(id=request.user.id)
    game_id = Game.objects.get(id=request.POST["game_id"])
    # Create a new Collection instance and save it
    add_to_collection = Collection()
    add_to_collection.owner = user_id
    add_to_collection.game_name = game_id
    add_to_collection.save()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def remove_game_from_collection(request):
    # Retrieve the Game_List object from which a game will be removed
    remove_from_collection = Collection.objects.get(
        game_name=int(request.POST["game_id"]), owner=request.user
    )
    # Delete the specific entry from the corresponding collection
    remove_from_collection.delete()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def my_lists(response):
    if response.user.is_authenticated:
        # Create new instance of NewList form
        new_list = NewList()
        # Retrieve all lists owned by current user
        current_lists = Game_List.objects.filter(creator=response.user)
        paginator = Paginator(current_lists, 16)
        page_number = response.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(
            response,
            "accounts/my_lists.html",
            context={"new_list": new_list, "current_lists": page_obj},
        )
    else:
        raise PermissionDenied


def create_list(response):
    if response.method == "POST" and response.user.is_authenticated:
        create_list_form = NewList(response.POST, response.FILES)
        if create_list_form.is_valid():
            # Create a new Game_List object
            created_list = Game_List()
            created_list.creator = response.user
            created_list.list_title = create_list_form.cleaned_data["title"]
            created_list.blurb = create_list_form.cleaned_data["blurb"]
            created_list.creation_date = datetime.datetime.now()
            created_list.list_image = create_list_form.cleaned_data[
                "hero_image"
            ]
            created_list.save()
            return HttpResponseRedirect(response.META["HTTP_REFERER"])


def add_to_list(request):
    # Retrieve the Game_List object to which a new game will be added
    new_list_item = Game_List.objects.get(id=request.POST["add_to_list"])
    # Append the new game to the game_list attribute of the Game_List object
    new_list_item.game_list.append(request.POST["game_id"])
    new_list_item.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def remove_game_from_list(request):
    # Retrieve the Game_List object from which a game will be removed
    new_list_item = Game_List.objects.get(id=request.POST["remove_from_list"])
    # Remove the specified game from the game_list
    # attribute of the Game_List object
    new_list_item.game_list.remove(int(request.POST["game_id"]))
    # Check if the game_list is empty and update the
    # published attribute accordingly
    if new_list_item.game_list == []:
        new_list_item.published = False
    new_list_item.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def publish_list(request):
    # Retrieve the Game_List object to be published
    publishing_list = Game_List.objects.get(id=request.POST["publish_list"])
    # Set the published attribute of the Game_List object to True
    publishing_list.published = True
    publishing_list.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def unpublish_list(request):
    # Retrieve the Game_List object to be unpublished
    publishing_list = Game_List.objects.get(id=request.POST["unpublish_list"])
    # Set the published attribute of the Game_List object to False
    publishing_list.published = False
    publishing_list.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def edit_list(request, pk):
    if request.method == "POST" and request.user.is_authenticated:
        edited_list = Game_List.objects.get(id=pk)
        edit_form = NewList(request.POST, request.FILES)
        if edit_form.is_valid():
            edited_list.list_title = edit_form.cleaned_data["title"]
            edited_list.blurb = edit_form.cleaned_data["blurb"]
            edited_list.list_image = edit_form.cleaned_data["hero_image"]
            edited_list.save()
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def delete_list(request):
    deleted_list = Game_List.objects.get(id=request.POST["list_id"])
    if request.user.is_authenticated and deleted_list.creator == request.user:
        deleted_list.delete()
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    else:
        return HttpResponseRedirect(request.META["HTTP_REFERER"])


def view_list(request, pk):
    # Retrieve the Game_List object to be viewed
    chosen_list = Game_List.objects.get(id=pk)
    # Retrieve the games in the chosen Game_List object
    games_in_list = Game.objects.filter(id__in=chosen_list.game_list)
    if request.user == chosen_list.creator:
        editForm = NewList()
        return render(
            request,
            "catalog/list_items.html",
            context={
                "chosen_list": chosen_list,
                "games_in_list": games_in_list,
                "editForm": editForm,
            },
        )
    else:
        return render(
            request,
            "catalog/list_items.html",
            context={
                "chosen_list": chosen_list,
                "games_in_list": games_in_list,
            },
        )


def remove_game(request, pk):
    # Retrieve the Game_List object from which a game will be removed
    containing_list = Game_List.objects.get(id=pk)
    # Remove the specified game from the game_list
    # attribute of the Game_List object
    containing_list.game_list.remove(int(request.POST["game_id"]))
    # Check if the game_list is empty and update the published
    # attribute accordingly
    if containing_list.game_list == []:
        containing_list.published = False
    containing_list.save()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def all_lists(request):
    # Retrieve all recently published Game_List objects
    # with non-empty game_list, sorted by creation_date
    all_lists = (
        Game_List.objects.filter(published=True)
        .exclude(game_list__exact=[])
        .order_by("-creation_date")
    )
    paginator = Paginator(all_lists, 16)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "catalog/all_lists.html",
        context={"all_recent_lists": page_obj},
    )


def genre_list(response):
    # Retrieve a list of all current genres
    all_genres = Genre.objects.all()
    return render(
        response, "catalog/genre_list.html", context={"all_genres": all_genres}
    )


def publisher_list(response):
    # Retrieve a list of all companies that have published games
    all_publishers = Company.objects.filter(published_list__isnull=False)
    return render(
        response,
        "companies/all_publishers.html",
        context={"all_publishers": all_publishers},
    )


def developer_list(response):
    # Retrieve a list of all companies that have developed games
    all_developers = Company.objects.filter(developed_list__isnull=False)
    return render(
        response,
        "companies/all_developers.html",
        context={"all_developers": all_developers},
    )


def developer_items(response, company_identifier):
    # Retrieve the company object based on the company identifier
    company = Company.objects.get(company_id=company_identifier)
    # Retrieve the list of games developed by the company
    game_list = Game.objects.filter(id__in=company.developed_list)
    # Call company updater to ensure all games are added to correct company
    company_updater.after_response(company.id)
    paginator = Paginator(game_list, 15)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "game_list": game_list,
        "company": company,
        "page_obj": page_obj,
    }
    return render(response, "companies/developers.html", context=context)


def publisher_items(response, company_identifier):
    # Retrieve the company object based on the company identifier
    company = Company.objects.get(company_id=company_identifier)
    # Retrieve the list of games published by the company
    game_list = Game.objects.filter(id__in=company.published_list)
    # Call company updater to ensure all games are added to correct company
    company_updater.after_response(company.id)
    paginator = Paginator(game_list, 15)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "game_list": game_list,
        "company": company,
        "page_obj": page_obj,
    }
    return render(response, "companies/publishers.html", context=context)


def genre_items(response, genre_identifier):
    # Retrieve the genre title based on the genre identifier
    genre_title = Genre.objects.get(genre_id=genre_identifier)
    # Retrieve the list of games that belong to the specified genre
    game_list = Game.objects.filter(genre_list__contains=[genre_identifier])
    paginator = Paginator(game_list, 15)
    page_number = response.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "game_list": game_list,
        "genre_title": genre_title,
        "page_obj": page_obj,
    }
    return render(response, "catalog/genre_items.html", context=context)
