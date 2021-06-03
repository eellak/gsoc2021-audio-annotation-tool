from django.contrib import admin

#relative import
from .models import Task

admin.site.register(Task)