from django.db import models

# Create your models here.
class User(models.Model):

    '''
    User class with basic attributes
    '''

    username = models.CharField(max_length=256, blank=False, primary_key=True)  #set the username as primary key
    email = models.EmailField(unique=True, blank=False)                         #set email as unique

    first_name = models.CharField(max_length=256, blank=False)
    last_name = models.CharField(max_length=256, blank=False)
    phone_number = models.CharField(max_length=256, blank=True)
    avatar = models.ImageField(blank=True)

    can_create_projects = models.BooleanField(default=False)                    #determines if a user is able to create projects (manager)