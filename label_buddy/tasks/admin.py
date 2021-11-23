from django.contrib import admin

# Relative import
from .models import (
    Task,
    Comment,
    Annotation
)


# Admin now has filters and search
class TaskAdmin(admin.ModelAdmin):

    """
    Task class for the admin site. list_display shows the fields
    displayed in the admin site.
    """

    search_fields = ["project"]
    list_display = ["id", "project", "file", "status", "review_status"]
    ordering = ("id",)
    list_filter = ["status", "review_status"]


class CommentAdmin(admin.ModelAdmin):

    """
    Comment class for the admin site. list_display shows the fields
    displayed in the admin site.
    """

    search_fields = ["reviewed_by"]
    list_display = ["id", "reviewed_by", "annotation", "created_at"]
    ordering = ("id",)


class AnnotationAdmin(admin.ModelAdmin):

    """
    Annotation class for the admin site. list_display shows the fields
    displayed in the admin site.
    """

    search_fields = ["user", "project"]
    list_display = ["id", "task", "project", "user", "created_at", "rejected_by_user", "hidden_by_user", "review_status"]
    ordering = ("id",)
    list_filter = ["rejected_by_user", "hidden_by_user"]


admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Annotation, AnnotationAdmin)
