from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = tuple(UserAdmin.fieldsets or ()) + (
        ("Rental role", {"fields": ("role",), },),)

    add_fieldsets = tuple(UserAdmin.add_fieldsets or ()) + (
        ("Additional fields", {"fields": ("email", "role",), },))

    list_display = ("username", "email", "role", "is_staff")
