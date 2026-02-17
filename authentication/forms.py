from django import forms
from allauth.account.forms import SignupForm,LoginForm
from .models import UserProfile,Prefrence,Category
class CustomSignupForm(SignupForm):
    
    email = forms.EmailField(max_length=30, label="Email",widget=forms.EmailInput(attrs={"placeholder":"e.g johndoe@gmail.com"}))
    first_name = forms.CharField(max_length=30, label="First Name",widget=forms.TextInput(attrs={"placeholder":"e.g John"}))
    last_name = forms.CharField(max_length=30, label="Last Name",widget=forms.TextInput(attrs={"placeholder":"e.g Doe"}))
    username = forms.CharField(max_length=15, label="Username",widget=forms.TextInput(attrs={"placeholder":"e.g john001"}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

class CustomLoginForm(LoginForm):
    
    def __init__(self,*args, **kwargs):
        super(CustomLoginForm,self).__init__(*args, **kwargs)
        for fieldname ,field in self.fields.items():
            if fieldname == "login":
                field.label = "Email/ Username"
            if fieldname == "login" and fieldname == "password":
                field.widget.attrs["class"] = "form-input"
           
            #print(field,)
        

    def login(self, *args, **kwargs):
        # Call the original login method to handle authentication
        user = super(CustomLoginForm, self).login(*args, **kwargs)

        # If "remember me" is not checked → make session expire when browser closes
        if not self.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)  # session ends on browser close
        else:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

        return user

class ProfileForm(forms.ModelForm):
    cover_photo = forms.ImageField(widget=forms.FileInput(attrs={"id":"coverInput","onchange":"handleCoverUpload(event)"}))
    profile_photo = forms.ImageField(widget=forms.FileInput(attrs={"id":"profileInput","onchange":"handleProfileUpload(event)"}))
   
    bio = forms.CharField(min_length= 300, widget=forms.Textarea(attrs={"class":"form-textarea",
                                                       "id":"bio",
                                                       "placeholder":"Tell us about yourself, your interests, and what you're passionate about...",
                                                       }))
    name_of_school = forms.CharField(widget=forms.TextInput(attrs={"class":"form-input","id":"schoolName","placeholder":"e.g., Harvard University"}))
    choices = [("High School","High School"),
               ("Associate Degree","Associate Degree"),
               ("Bachelor's Degree","Bachelor's Degree"),
               ("Master's Degree","Master's Degree"),
                ("PhD/Doctorate","PhD/Doctorate"),
                ( "Professional Certificate","Professional Certificate"),
                (  "Other","Other")
               ]
    level_of_education = forms.CharField(widget=forms.Select(choices=choices,attrs={"class":"form-select","id":"educationLevel"}))

    class Meta:
        model = UserProfile
        fields = ("cover_photo","profile_photo","bio","name_of_school","level_of_education")

class PrefrenceForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(),widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = Prefrence
        fields = ("category",)

                       