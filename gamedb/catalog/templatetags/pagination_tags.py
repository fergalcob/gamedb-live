from django import template
from urllib.parse import urlencode


register = template.Library()

@register.simple_tag
def url_replace (request, field, value):
    dict_ =  request.GET.copy()
    dict_[field] = value
    print(dict_)
    return dict_.urlencode()

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)