from django.contrib import admin
from .models import Article,Comment,Like,Category,Bookmark

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 2

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    model=Article
    inlines = [CommentInline]
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    model = Like

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    model = Category

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    model = Bookmark


# Register your models here.
