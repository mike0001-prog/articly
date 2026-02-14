from django.http import JsonResponse
from .models import Category
from authentication.models import Connection,Prefrence
from django.db.models import Q
from django import template
from .models import Bookmark,Like
#import re
from better_profanity import profanity
from django.core.cache import cache
import bleach
import base64
from django.utils.encoding import force_bytes,force_str

def check_authenticated_user(func):
    def wrapper(request):
        if not request.user.is_authenticated:
            return JsonResponse({"warning":"sigin or signup to continue"})
        return func(request)
    return wrapper

def custom_context(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        preference = Prefrence.objects.get(user=request.user).category.all()
        likes = Like.objects.filter(user=request.user).values_list("article_id",flat=True)
        bookmarks = Bookmark.objects.filter(user=request.user).values_list("article_id",flat=True)
        connected_user_ids = get_complex_data(request)
        print(connected_user_ids)
        context = {"category":categories,
                   "connections":connected_user_ids,
                    "saved_preferences":preference,"likes":likes,
               "bookmarks":bookmarks,}
    else:
        context = {"category":categories}
    return context

def filter_bad_words(text=""):
    clean_data =  profanity.censor(text, '*')
    is_profane =  profanity.contains_profanity(text)
    return clean_data,is_profane


def get_complex_data(request):
    data = cache.get(f'user_connections_{request.user}')
    
    if data is None:
        connections = Connection.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).values_list(
            'sender_id', 'receiver_id'
        )
        # print(connections)
        # s_e_t = set() 
        # for id in connections:
        #     for i in id:
        #         s_e_t.add(id)

        
        connected_user_ids = {
            uid for pair in connections for uid in pair
        }
        # print(connected_user_ids)
        connected_user_ids.discard(request.user.id)
        print(f"user_connections_{request.user}")
        cache.set(f'user_connections_{request.user}', connected_user_ids,None) # Cache for 1 hour
    return data


ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u",
    "h1", "h2", "h3",
    "ul", "ol", "li",
    "a", "blockquote", "code", "pre",
    "img"
]

ALLOWED_ATTRS = {
    "a": ["href", "title"],
    "img": ["src", "alt"]
}

def clean_html(html):
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True
    )

def decode_user_name(encoded_data):
    decoded_data = base64.urlsafe_b64decode(force_bytes(encoded_data))
    return force_str(decoded_data)