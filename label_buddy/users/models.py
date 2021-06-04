from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    
    '''
    User class inherited from Django User model
    '''

    #remove unnecessary fields
    groups = None
    user_permissions = None

    #additional fields
    can_create_projects = models.BooleanField(default=False, help_text='True if the user can create projects (be a manager)')
    phone_number = models.CharField(max_length=256, blank=True, help_text="User's phone number")
    avatar = models.ImageField(blank=True, help_text="User's avatar (image)")