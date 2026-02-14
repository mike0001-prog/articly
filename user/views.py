from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Article,Category,Like,Bookmark,Comment
from authentication.models import Connection,Prefrence
from django.contrib.auth.models import User
from django.http import JsonResponse
from .forms import ConnectUserForm,BookmarkForm,ArticleForm,CommentPageForm,CreateCommentForm,SearchForm
from django.views.decorators.http import require_POST
from .utils import filter_bad_words
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.db.models import Count, F,Sum,query
from django.core.paginator import Paginator
from django.core.cache import cache
from .utils import decode_user_name
from authentication.models import UserProfile
#from django.contrib.views
# Create your views here.

def home(request):
    # connect_user_form = ConnectUserForm
    categories = Category.objects.all()
    # user = User.objects.get(username= request.user)
    # article= Article.objects.filter().annotate(like_count=Count('like'))
    # likes = Like.objects.filter(user=request.user).values_list("article_id",flat=True)
    # bookmarks = Bookmark.objects.filter(user=request.user).values_list("article_id",flat=True)


    top_articles = (
        Article.objects
        .annotate(
            likes_count=Count("like", distinct=True),
            comments_count=Count("comment", distinct=True),
            engagement=F("likes_count") + F("comments_count"),
        )
        .order_by("-engagement")
        [:4]
    )
    if request.user.is_authenticated:
        preference = Prefrence.objects.get(user=request.user).category.all()
        preferences_ids = preference.values_list("id",flat=True)
        # category = Category.objects.exclude(id__in = preferences).values_list("id",flat=True)
        articles =(Article.objects.exclude(category__in = preferences_ids )
                .annotate(like_count=Count('like'))
                .annotate(comment_count=Count('comment')).select_related("user__userprofile") )
        context = {"category":categories ,
               "saved_preferences":preference,
               "articles":articles,
               "top_articles": top_articles,
            # "likes":likes,
            #    "bookmarks":bookmarks,
                "home":True
               }
        print(preference)
    else:
        articles = Article.objects.all()
        context = {
               "articles":articles,
               "top_articles": top_articles,
           
                "home":True
               }
  
    return render(request,"user/home.html",context)

@login_required
def profile(request,uid):
    decode_encoded_username = decode_user_name(uid)
    print(decode_encoded_username)
    user = User.objects.get(username=decode_encoded_username)
    user_profile = UserProfile.objects.get(user=user)
    articles =(Article.objects.filter(user = user )
                .annotate(like_count=Count('like'))
                .annotate(comment_count=Count('comment')).select_related("user__userprofile") )
    aggregate_likes_comment = Article.objects.filter(user = user ).aggregate(likes_sum=Count("like"),comment_sum=Count("comment"))
    print(aggregate_likes_comment)
    context = {"user_profile":user_profile,"articles":articles,"aggregate":aggregate_likes_comment}
    # print(user_profile)
    return render(request,"user/profile.html",context)

@require_POST
def connect(request):
    if request.method == "POST":
        form = ConnectUserForm(request.POST)
        print(form.errors)
        if form.is_valid():
            author = form.cleaned_data["author"]
            receiver = User.objects.get(username=author)
            connected = Connection.objects.filter(sender=request.user,receiver=receiver).exists()
            print(connected)
            if  connected:
                connected = Connection.objects.filter(sender=request.user,receiver=receiver).delete()
                return JsonResponse({"msg":"connected","connected":True})
            else:
                # connected.delete()
                Connection.objects.create(sender=request.user,receiver=receiver)
                return JsonResponse({"msg":"connected","connected":False})
    return JsonResponse({"msg":"bad request"})

# class ArticleCreateView(CreateView):
#     model = Article
#     template_name = "user/test.html"
#     form_class = ArticleForm
#     def form_valid(self, form):
#         return super().form_valid(form)


@login_required
def create_post(request):
    form = ArticleForm()
    if request.method == "POST":
        form = ArticleForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            pre_save = form.save(commit=False)
            pre_save.user = request.user
            filter_and_clean_bad_word = filter_bad_words(text=form.cleaned_data["content"])
            # cleaned_article_content = filter_and_clean_bad_word[0]
            is_bad_word = filter_and_clean_bad_word[1]
            if is_bad_word:
                pre_save.is_flagged = True
                pre_save.save()
                user = User.objects.get(username=request.user)
                user.flags+=1
                user.save()
            else:
                pre_save.save()

            # cleaned_category_id = form.cleaned_data["category"].id
            # category = Category.objects.get(id=cleaned_category_id)
            
            print(filter_and_clean_bad_word)
        #     created_article =  Article.objects.create(user=request.user,
        #                         title=form.cleaned_data["title"],
        #                         content= cleaned_article_content,
        #                         category=form.cleaned_data["category"]
        #                         )  
        #     if is_bad_word:
        #         created_article.is_flagged = True
        #         created_article.save()
        # # print(request.POST)
    context = {"form":form}
    return render(request,"user/create_post.html",context)

@require_POST
def like(request):
    if request.method == "POST":
        print(request.POST)
        post_id = request.POST["id"]
        article = Article.objects.get(id=post_id)
        liked = Like.objects.filter(user=request.user,article=article)
        if not liked:
            Like.objects.create(user=request.user,article=article)
            print("liked")
            return JsonResponse({"msg":"like","like":True})
        else:
            liked.delete()
            print("unliked")
            return JsonResponse({"msg":"unliked","like":False})
    return JsonResponse({"msg":"bad request"})

@require_POST
def bookmark(request):
    if request.method == "POST":
        print(request.POST)
        form = BookmarkForm(request.POST)
        if form.is_valid():
            article_id = form.cleaned_data["article_id"]
            article = Article.objects.get(id=article_id)
            bookmarked = Bookmark.objects.filter(user=request.user,article=article)
            if not bookmarked:
                Bookmark.objects.create(user= request.user,article= article)
                return JsonResponse({"msg":"bookmarked","bookmarked":True})
            else:
                bookmarked.delete()
                return JsonResponse({"msg":"unbookmarked","bookmarked":False})

    return JsonResponse({"msg":"bad request"})
@login_required
def comment(request,slug):
    if request.method == "POST":
        form = CommentPageForm(request.POST)
        if form.is_valid():
            article = Article.objects.get(slug=slug)
            test_form = CreateCommentForm()
            context = {"a":article,"test_form":test_form}
        else:
            return redirect("user_home")
    
    article = Article.objects.get(slug=slug)
    commented = Comment.objects.filter(article= article)
    print(commented)
    context = {"a":article,"commented":commented}
    return render(request,"user/comment.html",context)

def create_comment(request):
    if request.POST:
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            
            article_id = form.cleaned_data["article"]
            # print(type(article_id.id),"testing comments")
            filter_and_clean_bad_word = filter_bad_words(text=form.cleaned_data["comment"])
            cleaned_comment = filter_and_clean_bad_word[0]
            is_bad_comment = filter_and_clean_bad_word[1]
            print(filter_and_clean_bad_word)
            article = Article.objects.get(id=article_id.id)
            created_comment = Comment.objects.create(user=request.user,
                                                     comment= form.cleaned_data["comment"],
                                                       article=article)
            if is_bad_comment:
                created_comment.is_flagged = True
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.flags+=1
                user_profile.save()
                created_comment.save()
    return redirect("comment_page",slug=article.slug)

def bookmarks_page(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    context = {"bookmarks":bookmarks}
    return render(request,"user/bookmark.html",context)

@require_POST
@csrf_exempt
def search(request):
    if request.method == "POST":
        print(request.POST)
        form = SearchForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data["search_query"]
            if search_query:
                articles = Article.objects.filter(
                    Q(title__istartswith=search_query) | 
                    Q(title__icontains=search_query))[:5]
                
                # print(articles_dict)
                users = User.objects.filter(
                    Q(username__icontains=search_query) |
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query)
                )[:5]
            # articles =  Article.objects.filter(Q(name__icontains=search_query))
            # articles = Article.objects.prefetch_related(Q(name__icontains=search_query))
            articles_dict = {f"articles":{"title":a.title,"slug":a.slug} for a in articles}
            print(articles_dict)
            return JsonResponse(articles_dict)
    return JsonResponse({})
@require_POST
def search_page(request):
    if request.method == "POST":
        print(request.POST)
        form = SearchForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data["search_query"]
            articles = Article.objects.filter(
                    Q(title__istartswith=search_query) | 
                    Q(title__icontains=search_query))
            # articles = Article.objects.prefetch_related(Q(name__contains=search_query))
            context = {"results":articles}
            return render(request,"user/search.html",context)

def test(request):
    return render(request,"user/test.html")

def explore(request):
    user = request.user
    # p=Prefrence.objects.filter(user=user).prefetch_related("category").all()
    articles = Article.objects.filter().annotate(like_count=Count('like'))

    # likes = Like.objects.filter(user=request.user).values_list("article_id",flat=True)
    # bookmarks = Bookmark.objects.filter(user=request.user).values_list("article_id",flat=True)
    if request.user.is_authenticated:
       preferences = Prefrence.objects.get(user=request.user).category.all().values_list("id",flat=True)
    # category = Category.objects.exclude(id__in = preferences).values_list("id",flat=True)
    # articles = Article.objects.exclude(category__in = preferences )
    print(articles)
    context = {"articles":articles}
    return render(request,"user/explore.html",context)
    