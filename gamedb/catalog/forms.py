from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from tinymce.widgets import TinyMCE
from tinymce import models as tinymce_models
from tinymce.models import HTMLField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div
from crispy_forms.bootstrap import InlineRadios
from star_ratings.models import Rating
from catalog.models import Game_List