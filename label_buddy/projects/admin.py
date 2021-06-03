from django.contrib import admin

#relative import
from .models import Project, Label

admin.site.register(Project)
admin.site.register(Label)