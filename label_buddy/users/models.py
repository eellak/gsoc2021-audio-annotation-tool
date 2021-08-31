import os

from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """
    User class inherited from Django User model
    """

    #remove unnecessary fields
    # groups = None
    # user_permissions = None

    #additional fields
    name = models.CharField(max_length=256, default="", db_index=True, help_text='Users full name')
    can_create_projects = models.BooleanField(default=False, help_text='True if the user can create projects (be a manager)')
    phone_number = models.CharField(max_length=256, blank=True, help_text="User's phone number")
    avatar = models.ImageField(upload_to='images', blank=True, help_text="User's avatar (image)")

    #How to display projects in admin
    def __str__(self):
        return '%s' % (self.username)
        if not self.name and not self.email:
            return '%s' % (self.username)
        else:
            if self.name and self.email:
                return '%s - %s' % (self.name, self.email)
            elif self.name:
                return '%s' % (self.name)
            else:
                return '%s' % (self.email)

@receiver(pre_save, sender=User)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding user object is updated
    with new file.
    """
    pk = instance.pk
    if not pk:
        return False

    try:
        old_avatar = User.objects.get(pk=pk).avatar
    except User.DoesNotExist:
        return False

    if old_avatar:
        new_avatar = instance.avatar
        if not old_avatar == new_avatar:
            if os.path.isfile(old_avatar.path):
                os.remove(old_avatar.path)

@receiver(pre_save, sender=User)
def set_users_avatar(sender, instance, **kwargs):
    """
    If user's avatar is not specified
    set it to the unknown icon user
    """
    if not instance.avatar:
        user_avatar = open(os.path.join(settings.BASE_DIR, 'static/images/user/user.jpg'), "rb")
        instance.avatar.save('user.jpg', File(user_avatar))