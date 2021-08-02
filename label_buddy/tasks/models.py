import os

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from enumchoicefield import ChoiceEnum, EnumChoiceField
from url_or_relative_url_field.fields import URLOrRelativeURLField

from users.models import User
from projects.models import Project

# Create your models here.

class Status(ChoiceEnum):
    """
    Enum class for task status
    """

    labeled = "Labeled"
    unlabeled = "Unlabeled"

class Review_status(ChoiceEnum):
    """
    Enum class for task review_status
    """

    unreviewed = "Unreviewed"
    reviewed = "Reviewed"
    commented = "Commented"


class Task(models.Model):
    """
    Task class to store audio (image or video) files for each project.
    Tasks will be completed (annotated) by annotatos
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text='Project to which the task belongs')
    file = models.FileField(upload_to='audio', blank=True, null=True, help_text='Local file uploaded')
    url = URLOrRelativeURLField(blank=True, help_text='URL for a file')

    extra = models.JSONField(blank=True, null=True, default=None, help_text='Extra info about the task')
    status = EnumChoiceField(Status, default=Status.unlabeled, help_text='If the task is annotated status must be labeled else unlabeled')
    review_status = EnumChoiceField(Review_status, default=Review_status.unreviewed, help_text='Status for reviews')

    # assigned_to = models.ManyToManyField(User, blank=True, related_name='task_annotators', help_text='Annotators who will annotate the task')

    class Meta:
        ordering = ['-id']

    #We ensure that even one of file or url should have a value
    def clean(self):
        if not self.file and not self.url:  # This will check for None or Empty
            raise ValidationError({'file': 'Even one of file or url should have a value.'})

    def __str__(self):
        return 'Task: %d - project: %s' % (self.id, self.project)

#Classes for Annotation and Comments by reviewers

class Comment(models.Model):
    """
    Comment class for comments done by reviewers
    Annotators will be able to see the comments on their annotations
    """

    comment = models.TextField(blank=False, help_text='Comment for an annotation')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, help_text='User creating the comment')
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of comment creation')

    def __str__(self):
        return 'Comment from %s' % (self.user)


class Annotation(models.Model):
    """
    Annotation class for annotations done by annotators
    Annotation format will be in JSON format
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False, help_text='Task to which the annotation belongs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, help_text='Project to which the annotation belongs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='annotation_user', help_text='User who made the annotation')

    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of annotation creation')
    updated_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of update')

    result = models.JSONField(blank=True, null=True, help_text='The result of the annotation in JSON format')

    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='annotation_reviewer', help_text='Reviewer who made the review')
    reviewed_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of a review')

    rejected_by_user = models.BooleanField(default=False, help_text='Annotation rejected by user true/false')
    hidden_by_user = models.BooleanField(default=False, help_text='Hidden by users true/false')

    comment = models.ManyToManyField(Comment, blank=True, related_name='annotation_comment', help_text='Comments done for the annotation')

    class Meta:
        unique_together = ('user', 'task',)

    def __str__(self):
        return 'Annotation %d - project: %s' % (self.id, self.project)


# When an annotation is created, the task to which it belongs must be set a labeled (Task.status = labeled)
@receiver(post_save, sender=Annotation)
def make_task_labeled(sender, instance, created, **kwargs):

    if created:
        task = instance.task
        task.status = Status.labeled
        task.save()

# after deleting an annotation check task and if has no other annotation mark it as unlabeled
@receiver(pre_delete, sender=Annotation)
def mark_task_unlabeled(sender, instance, **kwargs):

    try:
        task_annotation = instance.task
    except Annotation.DoesNotExist:
        return False

    task_annotations = Annotation.objects.filter(task=task_annotation).count() - 1
    if task_annotations == 0:
        task_annotation.status = Status.unlabeled
        task_annotation.save()


@receiver(pre_delete, sender=Task)
def auto_delete_files(sender, instance, **kwargs):
    """
    Delete task's file from system after delete
    """

    try:
        task_file = instance.file
    except Task.DoesNotExist:
        return False

    if task_file:
        if os.path.isfile(task_file.path):
            os.remove(task_file.path)