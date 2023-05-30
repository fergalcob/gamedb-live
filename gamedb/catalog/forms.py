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


class ReviewBox(forms.Form):
    title = forms.CharField(max_length=200,required=True)
    ratings = [('','')]
    test_rating = Rating()
    Review=forms.IntegerField(label='Review', widget=forms.RadioSelect(choices=ratings),required=True)
    comment = forms.CharField(widget=TinyMCE(attrs={'cols': 125, 'rows': 5, "forced_root_block": 'p',"newline_behavior": 'block'}),required=True)
    class Meta:
        model = MyModel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
                Div(
            'title',
            'comment'
                ))

class CommentBox(forms.Form):
    title = forms.CharField(max_length=200)
    comment = forms.CharField(widget=TinyMCE(attrs={'cols': 120, 'rows': 5,'theme':'advanced','force_p_newlines' : False, 'forced_root_block': False,'newline_behavior': 'block'}))
    class Meta:
        model = MyModel
        fields = '__all__'
