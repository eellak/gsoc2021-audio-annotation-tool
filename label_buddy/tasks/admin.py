from django.contrib import admin

#relative import
from .models import (
    Task, 
    Comment, 
    Annotation
)

#Admin now has filters and search

class TaskAdmin(admin.ModelAdmin):
    search_fields = ["project"]
    list_display = ["id", "project", "status", "review_status"]
    ordering = ("id",)
    list_filter = ["status", "review_status"]

class CommentAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ["id", "user", "created_at"]
    ordering = ("id",)

class AnnotationAdmin(admin.ModelAdmin):
    search_fields = ["user", "project"]
    list_display = ["id", "task", "project", "user", "created_at", "rejected_by_user", "hidden_by_user"]
    ordering = ("id",)
    list_filter = ["rejected_by_user", "hidden_by_user"]


admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Annotation, AnnotationAdmin)