from django.db import models
from enumchoicefield import ChoiceEnum, EnumChoiceField
from url_or_relative_url_field.fields import URLOrRelativeURLField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text='Project to which the task belongs')
    file = models.FileField(blank=True, null=True, help_text='Local file uploaded')
    url = URLOrRelativeURLField(blank=True, help_text='URL for a file')

    extra = models.JSONField(blank=True, null=True, default=None, help_text='Extra info about the task')
    status = EnumChoiceField(Status, default=Status.unlabeled, help_text='If the task is annotated status must be labeled else unlabeled')
    review_status = EnumChoiceField(Review_status, default=Review_status.unreviewed, help_text='Status for reviews')

    assigned_to = models.ManyToManyField(User, blank=True, related_name='task_annotators', help_text='Annotators who will annotate the task')


    #We ensure that even one of file or url should have a value
    def clean(self):
        if not self.file and not self.url:  # This will check for None or Empty
            raise ValidationError({'file': 'Even one of file or url should have a value.'})

    def __str__(self):
        return 'Task: %d - project: %s' % (self.id, self.project)

#Classes for Annotation and Comments by reviewers

class Comment(models.Model):

    '''
    Comment class for comments done by reviewers
    Annotators will be able to see the comments on their annotations
    '''

    comment = models.TextField(blank=False, help_text='Comment for an annotation')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, help_text='User creating the comment')
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of comment creation')

    def __str__(self):
        return 'Comment from %s' % (self.user)


class Annotation(models.Model):

    '''
    Annotation class for annotations done by annotators
    Annotation format will be in JSON format
    '''

    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False, help_text='Task to which the annotation belongs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, help_text='Project to which the annotation belongs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='annotation_user', help_text='User who made the annotation')

    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of annotation creation')
    updated_at = models.DateTimeField(blank=False, help_text='Date and time of update')

    result = models.JSONField(blank=True, null=True, help_text='The result of the annotation in JSON format')

    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='annotation_reviewer', help_text='Reviewer who made the review')
    reviewed_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of a review')

    rejected_by_user = models.BooleanField(default=False, help_text='Annotation rejected by user true/false')
    hidden_by_user = models.BooleanField(default=False, help_text='Hidden by users true/false')

    comment = models.ManyToManyField(Comment, blank=True, related_name='annotation_comment', help_text='Comments done for the annotation')

    def __str__(self):
        return 'Annotation %d - project: %s' % (self.id, self.project)


#When an annotation is created, the task to which it belongs must be set a labeled (Task.status = labeled)
@receiver(post_save, sender=Annotation)
def make_task_labeled(sender, instance, created, **kwargs):

    if created:
        task = instance.task
        task.status = Status.labeled
        task.save()