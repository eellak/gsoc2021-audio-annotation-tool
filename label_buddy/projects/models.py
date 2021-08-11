import os

from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from colorfield.fields import ColorField
from enumchoicefield import ChoiceEnum, EnumChoiceField

from users.models import User
#Create your models here.


class Project_type(ChoiceEnum):

    '''
    Enum class for project type (annotation of audio image or video files)
    '''

    audio = "Audio annotation"
    image = "Image annoation"
    video = "Video annotation"


class Label(models.Model):

    '''
    Label class for labels created to annotate audio files
    '''

    name = models.CharField(max_length=256, blank=False, primary_key=True, help_text='Name of the label')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', help_text='Parent label of the label (optional)')
    color = ColorField(blank=True, unique=True, default='#74deed', help_text='Color given to the label (optional)')

    #How to display labels in admin
    def __str__(self):
        return '%s' % (self.name)



class Project(models.Model):

    '''
    Project class for projects created by managers (can_create_projects=True)
    Contains basic information about a specific project
    '''


    title = models.CharField(max_length=256, blank=True, null=True, default='', help_text='Project title')

    description = models.TextField(blank=True, null=True, default='', help_text='Project description')
    instructions = models.TextField(blank=True, null=True, default='', help_text='Project instructions')
    logo = models.ImageField(upload_to='images', blank=True, help_text='Project logo')
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of project creation')

    users_can_see_other_queues = models.BooleanField(default=False, help_text='<b>If false, annotators will see only tasks assigned to them</b>')

    labels = models.ManyToManyField(Label, blank=False, help_text='Labels used by annotators to annotate')
    reviewers = models.ManyToManyField(User, blank=True, related_name='project_reviewer', help_text='Reviewers who will review annotations')
    annotators = models.ManyToManyField(User, blank=True, related_name='project_annotator', help_text='Annotators for the project')
    managers = models.ManyToManyField(User, blank=True, related_name='project_manager', help_text='Managers for the project')

    project_type = EnumChoiceField(Project_type, default=Project_type.audio, help_text='Specify the type of the annotation (Audio, image or Video)')

    class Meta:
        ordering = ['id']
    
    #How to display projects in admin
    def __str__(self):
        return '%s' % (self.title)

@receiver(pre_save, sender=Project)
def auto_delete_logo_on_change(sender, instance, **kwargs):
    """
    Deletes old logo from filesystem
    when corresponding project object is updated
    with new file.
    """
    pk = instance.pk
    if not pk:
        return False

    try:
        old_logo = Project.objects.get(pk=pk).logo
    except Project.DoesNotExist:
        return False

    if old_logo:
        new_logo = instance.logo
        if not old_logo == new_logo:
            if os.path.isfile(old_logo.path):
                os.remove(old_logo.path)


@receiver(pre_delete, sender=Project)
def auto_delete_logo_on_delete(sender, instance, **kwargs):
    """
    Delete project's logo from system after delete
    """

    try:
        project_logo = instance.logo
    except Project.DoesNotExist:
        return False

    if project_logo:
        if os.path.isfile(project_logo.path):
            os.remove(project_logo.path)


@receiver(pre_save, sender=Project)
def set_users_avatar(sender, instance, **kwargs):
    """
    If project's logo is not specified
    set it to the unknown icon project
    """
    if not instance.logo:
        project_logo = open(os.path.join(settings.BASE_DIR, 'static/images/project_logo.png'), "rb")
        instance.logo.save('project_logo.png', File(project_logo))