from django.shortcuts import render,redirect
# from allauth.account.views import LoginView,SignupView
from user.models import Category
from django.views.decorators.csrf import csrf_exempt
from user.forms import ArticleForm
from .forms import ProfileForm,PrefrenceForm
from django.contrib.auth.decorators import login_required
from .models import Prefrence,UserProfile 
from django.http import JsonResponse
from django.contrib import messages

def prefrences(request):
    preference_instance = Prefrence.objects.get(user=request.user)
    form = PrefrenceForm(instance=preference_instance or None)
    if request.method == "POST":
        data = request.POST
        form = PrefrenceForm(request.POST,instance=preference_instance or None)
        print(data)
        print(form.is_valid())
        if form.is_valid():
            pre_save =  form.save(commit=False)
            pre_save.user = request.user
            pre_save.save()
            form.save_m2m()
        return JsonResponse({"msg":"prefrences updated"})
    preference = Prefrence.objects.get(user=request.user).category.all()
    category = Category.objects.all()
    context = {"category":category,"form":form,"preference":preference}
    return render(request,"account/prefrences.html",context)


def landing_page(request):
    return render(request, "account/landing.html")
@login_required
def update_profile(request):
    profile = UserProfile.objects.filter(user=request.user)
    if profile:
        profile = UserProfile.objects.get(user=request.user)
    
        form = ProfileForm(instance=profile or None)
    else:
        form = ProfileForm()
    if request.method =="POST":
        if profile:
            profile = UserProfile.objects.get(user=request.user)
            form = ProfileForm(request.POST,request.FILES,instance=profile)
            print(form.is_valid())
        else:
            form = ProfileForm(request.POST,request.FILES)
        if form.is_valid():
            print(form.is_valid())
            form.save()
            messages.success(request,"sucessfully updated your profile")
            return redirect("update_profile")
    context = {"form":form,"profile":profile}
    return render(request,"account/update_profile.html",context)
# from .forms import CustomSignupForm,CustomLoginForm
# # Create your views here.
# def login(request):
#     form = CustomLoginForm
#     if request.method == "POST":
#         CustomLoginForm(request.POST)
#     context = {"form": form}
#     return render(request,"auth/login.html",context)


# def signup(request):
#     context = {"form":CustomSignupForm}
#     return render(request,"auth/signup.html",context)

# class CustomLogin(LoginView):
#     template_name = "account/.html"
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def login(self):
#         return super.login(self.user)

