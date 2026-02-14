from django import forms
from .models import Article,Category,Comment
from authentication.models import Connection
"""
all forms inherit forms.Form like ConnectUserForm,
BookmarkForm,CommentPageForm ensure that the views that 
they are used in validate all input an
"""
from django_ckeditor_5.widgets import CKEditor5Widget
from .utils import clean_html

class ArticleForm(forms.ModelForm):
    title = forms.CharField(max_length=30,widget=forms.TextInput())
    content = CKEditor5Widget()
    category = forms.ModelChoiceField(queryset=Category.objects.all(),widget=forms.RadioSelect)
    class Meta:
        model = Article
        fields = ("title","content","category")
    
    def clean(self):
        clean_html(self.cleaned_data["content"])
        super().clean()

class ConnectUserForm(forms.Form):
    author = forms.CharField(widget=forms.HiddenInput())

class BookmarkForm(forms.Form):
    article_id = forms.IntegerField(min_value=1,widget=forms.HiddenInput())

class CommentPageForm(forms.Form):
    article_id = forms.CharField(max_length=255,widget=forms.HiddenInput())


class CreateCommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.TextInput())
    article = forms.ModelChoiceField(queryset=Article.objects.all(),widget=forms.HiddenInput())
    class Meta:
        model = Comment
        fields = ("comment","article")
    # def __init__(self, *args, **kwargs)
    #     super(ConnectUserForm,self).__init__(*args, **kwargs)
    #     self.user = kwargs.pop("request")
    #     for field_names,field in self.fields.items():
    #         field.widget.attrs = self.user
    # class Meta:
    #     model = Connection
    #     fields = ["reciever"]

class SearchForm(forms.Form):
    search_query = forms.CharField(max_length=25,widget=forms.TextInput())
    
