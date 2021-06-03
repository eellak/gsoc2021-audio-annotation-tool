from django.contrib import admin

#relative import
from .models import User

admin.site.register(User)