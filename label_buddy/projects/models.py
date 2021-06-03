from colorfield.fields import ColorField
from enumchoicefield import ChoiceEnum, EnumChoiceField
from django.db import models

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

    name = models.CharField(max_length=256, blank=False, primary_key=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')  #parent label
    color = ColorField(blank=True, default='#FF0000')



class Project(models.Model):

    '''
    Project class for projects created by managers (can_create_projects=True)
    Contains basic information about a specific project
    '''


    title = models.CharField(max_length=256, blank=False, null=False, default='', primary_key=True)

    description = models.TextField(blank=True, null=True, default='', help_text='Project description')
    instructions = models.TextField(blank=True, null=True, default='', help_text='Project instructions')
    logo = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of project creation')

    users_can_see_other_queues = models.BooleanField(default=False)                         #users can see which tasks are assinged to other users for this specific project

    labels = models.ManyToManyField(Label, blank=False)                                     #each project has a set of labels which can be used by annotators to annotate
    reviewers = models.ManyToManyField(User, blank=True, related_name='project_reviewer')   #each project has a set of reviewers (users) who can review annotations
    annotators = models.ManyToManyField(User, blank=True, related_name='project_annotator') #each project has a set of annotators who can annotate it's audio files
    managers = models.ManyToManyField(User, blank=True, related_name='project_manager')     #each project has a set of managers who can change it's configurations

    project_type = EnumChoiceField(Project_type, default=Project_type.audio)                #type of annoation (default audio annoation tool)

