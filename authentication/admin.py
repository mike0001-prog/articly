from django.contrib import admin
from .models import Connection,UserCategory,UserProfile,Prefrence
# Register your models here.
@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    model = Connection

@admin.register(UserCategory)
class UserCategoryAdmin(admin.ModelAdmin):
    model = UserCategory

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile

@admin.register(Prefrence)
class PrefrenceAdmin(admin.ModelAdmin):
    model = Prefrence

