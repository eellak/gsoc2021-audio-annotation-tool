from django.db import models
from enumchoicefield import ChoiceEnum, EnumChoiceField
from url_or_relative_url_field.fields import URLOrRelativeURLField
from django.core.exceptions import ValidationError

from users.models import User
from projects.models import Project

# Create your models here.

class Status(ChoiceEnum):

    '''
    Enum class for task status
    '''

    labeled = "Labeled task"
    unlabeled = "Unlabeled task"

class Review_status(ChoiceEnum):

    '''
    Enum class for task review_status
    '''

    unreviewed = "Unreviewed task"
    reviewed = "Reviewed task"
    commented = "Commented task"


class Task(models.Model):

    '''
    Task class to store audio (image or video) files for each project.
    Tasks will be completed (annotated) by annotatos
    '''

    project = models.ForeignKey(Project, on_delete=models.CASCADE)                          #project to which the task belongs
    file = models.FileField(blank=True, null=True)
    url = URLOrRelativeURLField(blank=True)

    extra = models.JSONField(blank=True, null=True, default=None)                           #extra info about the task
    status = EnumChoiceField(Status, default=Status.unlabeled)
    review_status = EnumChoiceField(Review_status, default=Review_status.unreviewed)

    assigned_to = models.ManyToManyField(User, blank=True, related_name='task_annotators')


    #We ensure that even one of file or url should have a value
    def clean(self):
        if not self.file and not self.url:  # This will check for None or Empty
            raise ValidationError({'file': 'Even one of file or url should have a value.'})


#to create AssingedAudio class for future use