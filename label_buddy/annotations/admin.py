from django.contrib import admin

#relative import
from .models import Comment, Annotation

admin.site.register(Comment)
admin.site.register(Annotation)
