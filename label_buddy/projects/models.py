from django.db import models
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
    color = ColorField(blank=True, unique=True, default='#FF0000', help_text='Color given to the label (optional)')

    #How to display labels in admin
    def __str__(self):
        return '%s' % (self.name)



class Project(models.Model):

    '''
    Project class for projects created by managers (can_create_projects=True)
    Contains basic information about a specific project
    '''


    title = models.CharField(max_length=256, blank=False, null=False, default='', help_text='Project title')

    description = models.TextField(blank=True, null=True, default='', help_text='Project description')
    instructions = models.TextField(blank=True, null=True, default='', help_text='Project instructions')
    logo = models.ImageField(blank=True, help_text='Project logo')
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of project creation')

    users_can_see_other_queues = models.BooleanField(default=False, help_text='If true, users can see which tasks are assinged to other users for this specific project')

    labels = models.ManyToManyField(Label, blank=False, help_text='Labels used by annotators to annotate')
    reviewers = models.ManyToManyField(User, blank=True, related_name='project_reviewer', help_text='Reviewers who will review annotations')
    annotators = models.ManyToManyField(User, blank=True, related_name='project_annotator', help_text='Annotators for the project')
    managers = models.ManyToManyField(User, blank=True, related_name='project_manager', help_text='Managers for the project')

    project_type = EnumChoiceField(Project_type, default=Project_type.audio, help_text='Specify the type of the annotation (Audio, image or Video)')

    #How to display projects in admin
    def __str__(self):
        return '%s' % (self.title)

