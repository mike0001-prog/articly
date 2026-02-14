from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} "
from django.utils.text import slugify
class Article(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = CKEditor5Field('Text', config_name='extends')
    time_created = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,default=None)
    slug = models.SlugField(unique=True,max_length=255)

    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    article = models.ForeignKey(Article,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} like"

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.TextField()
    article = models.ForeignKey(Article,on_delete=models.CASCADE)
    is_flagged = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} comment"

class Bookmark(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    article = models.ForeignKey(Article,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} bookmark"



