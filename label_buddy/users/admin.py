from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

# Relative import
from .models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ["email", "username"]
    exclude = (
        "user_permissions",
        "title",
        "groups",
        "password",
        "last_login",
        "is_featured",
        "location",
        "media_count",
        "is_active",
    )
    list_display = [
        "id",
        "name",
        "username",
        "email",
        "first_name",
        "last_name",
        "can_create_projects",
        "phone_number",
        "avatar",
        "date_joined",
    ]
    list_filter = ["can_create_projects", ]
    ordering = ("id",)


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)  # Remove groups from admin
