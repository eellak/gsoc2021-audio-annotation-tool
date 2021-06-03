from django.db import models

from users.models import User
from tasks.models import Task
from projects.models import Project

# Create your models here.

class Comment(models.Model):

    '''
    Comment class for comments done by reviewers
    Annotators will be able to see the comments on their annotations
    '''

    comment = models.TextField(blank=False, help_text='Comment for an annotation')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of comment creation')


class Annotation(models.Model):

    '''
    Annotation class for annotations done by annotators
    Annotation format will be in JSON format
    '''

    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False)                                   #task to which the annotation belongs
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False)                             #project to which the annotation belongs
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='annotation_user')   #user who annotated

    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of annotation creation')
    updated_at = models.DateTimeField(blank=False, help_text='Date and time of update')

    result = models.JSONField(blank=True, null=True)

    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='annotation_reviewer')
    reviewed_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of a review')

    rejected_by_user = models.BooleanField(default=False)
    hidden_by_user = models.BooleanField(default=False)

    comment = models.ManyToManyField(Comment, blank=True, related_name='annotation_comment')

