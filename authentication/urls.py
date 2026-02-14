from django.urls import path,include
from . import views
urlpatterns = [
    
    path('prefrence/',views.prefrences,name="preferences"),
    path("settings/profile/", views.update_profile, name="update_profile")
]