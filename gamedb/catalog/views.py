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
