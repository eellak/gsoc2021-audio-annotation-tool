from django.contrib import admin

#relative import
from .models import Task, Comment, Annotation

admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Annotation)