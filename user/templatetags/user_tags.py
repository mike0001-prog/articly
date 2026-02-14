from django import template
import base64
from django.utils.encoding import force_bytes,force_str
register = template.Library()

@register.filter
def truncate(value,arg):
    words = value.split()[:arg]
    return ' '.join(words)

@register.filter
def count(value):
    count = len(value.split())
    return count 

@register.filter
def generate_token(data):
    encoded_bytes = base64.urlsafe_b64encode(force_bytes(data))
    return force_str(encoded_bytes)

# def len()

# @register.inclusion_tag("components/article.html", takes_context=True)
# def render_post(context, post):
#     return {
#         "post": post,
#         "likes": context["likes"],
#         "bookmarks": context["bookmarks"],
#         "connections": context["connections"],
#         "request": context["request"],
#     }
