from django.contrib import admin

#relative import
from .models import Project, Label

#Admin now has filters and search

class ProjectAmdin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["id", "title", "created_at", "users_can_see_other_queues", "project_type"]
    ordering = ("created_at",)
    list_filter = ["users_can_see_other_queues", "project_type"]

class LabelAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]

admin.site.register(Project, ProjectAmdin)
admin.site.register(Label, LabelAdmin)