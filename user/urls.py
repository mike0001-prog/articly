from user import views
from django.urls import path
urlpatterns = [
    path('home/', views.home,name="user_home"),
    path('profile/<str:uid>',views.profile,name="user_profile"),
    path("create_post/", views.create_post, name="create_post"),
    path("like_post/", views.like, name="like_post"),
    path("bookmark_post/", views.bookmark,name="bookmark_post"),
    path("connect/", views.connect, name="connect_user"),
    path("comment_page/<str:slug>", views.comment, name="comment_page"),
    path("create_comment/", views.create_comment, name="create_comment"),
    path("bookmarks/", views.bookmarks_page, name="bookmarks_page"),
    path("search/",views.search,name="search"),
    path("search_page/",views.search_page,name="search_page"),
    path("test/", views.test, name="test"),
    path("explore/", views.explore, name="explore"),
    path("connections/", views.connections,name="connections_list")

]