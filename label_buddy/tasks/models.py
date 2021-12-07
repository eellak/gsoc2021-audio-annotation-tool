import os
import jsonfield

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver
from enumchoicefield import ChoiceEnum, EnumChoiceField
from url_or_relative_url_field.fields import URLOrRelativeURLField

from users.models import User
from projects.models import Project


def get_review(annotation):

    """
    Get a review done for an annotation (if exists).
    """

    try:
        review = Comment.objects.get(annotation=annotation)
        return review
    except Comment.DoesNotExist:
        return None


# Create your models here
class Status(ChoiceEnum):

    """
    Enum class for task status.
    """

    labeled = "Labeled"
    unlabeled = "Unlabeled"


class Review_status(ChoiceEnum):

    """
    Enum class for task review_status.
    """

    unreviewed = "Unreviewed"
    reviewed = "Reviewed"


class Annotation_status(ChoiceEnum):

    """
    Review status for each annotation.
    """

    approved = "Approved"
    rejected = "Rejected"
    no_review = "Unreviewed"


class Task(models.Model):

    """
    Task class to store audio (image or video) files for each project.
    Tasks will be completed (annotated) by annotatos.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text='Project to which the task belongs')
    file = models.FileField(upload_to='audio', blank=True, null=True, help_text='Local file uploaded')
    original_file_name = models.CharField(max_length=256, blank=True, null=True, default='', help_text='Task file original file name')
    url = URLOrRelativeURLField(blank=True, help_text='URL for a file')

    extra = jsonfield.JSONField(blank=True, null=True, default=None, help_text='Extra info about the task')
    status = EnumChoiceField(Status, default=Status.unlabeled, help_text='If the task is annotated status must be labeled else unlabeled')
    review_status = EnumChoiceField(Review_status, default=Review_status.unreviewed, help_text='Status for reviews')

    assigned_to = models.ManyToManyField(User, blank=True, related_name='task_annotators', help_text='Annotators who will annotate the task')

    class Meta:
        ordering = ['-id']

    # We ensure that even one of file or url should have a value
    def clean(self):
        if not self.file and not self.url:  # This will check for None or Empty
            raise ValidationError({'file': 'Even one of file or url should have a value.'})

    def __str__(self):
        return 'Task: %d - project: %s' % (self.id, self.project)


class Annotation(models.Model):

    """
    Annotation class for annotations done by annotators.
    Annotation format will be in JSON format.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=False, help_text='Task to which the annotation belongs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, help_text='Project to which the annotation belongs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='annotation_user', help_text='User who made the annotation')

    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of annotation creation')
    updated_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of update')

    result = jsonfield.JSONField(blank=True, null=True, help_text='The result of the annotation in JSON format')

    reviewed_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of a review')

    rejected_by_user = models.BooleanField(default=False, help_text='Annotation rejected by user true/false')
    hidden_by_user = models.BooleanField(default=False, help_text='Hidden by users true/false')

    review_status = EnumChoiceField(Annotation_status, default=Annotation_status.no_review, help_text='Status for annotation review')

    class Meta:
        unique_together = ('user', 'task',)

    def __str__(self):
        return 'Annotation %d - project: %s' % (self.id, self.project)


class Comment(models.Model):

    """
    Comment class for comments done by reviewers.
    Annotators will be able to see the comments on their annotations.
    """

    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, related_name='annotation_reviewer', help_text='Reviewer who made the review')
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, blank=False, related_name='annotation_reviewed', help_text='Annotation reviewed')

    comment = models.TextField(blank=False, help_text='Comment for an annotation')
    created_at = models.DateTimeField(auto_now=True, help_text='Date and time of comment creation')
    updated_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of update')

    class Meta:
        unique_together = ('reviewed_by', 'annotation',)

    def __str__(self):
        return 'Comment from %s' % (self.reviewed_by)


# SIGNALS
@receiver(post_save, sender=Annotation)
def make_task_labeled(sender, instance, created, **kwargs):

    """
    When an annotation is saved, mark the corresponding task as labeled (if it's the first annotation for the task).
    """

    task = instance.task
    if created and task.status == Status.unlabeled:
        task = instance.task
        task.status = Status.labeled
        task.save()


@receiver(post_save, sender=Comment)
def check_if_task_reviewed(sender, instance, created, **kwargs):

    """
    If all annotations which belong to the task are reviewed, then make task reviewed.
    """

    task = instance.annotation.task
    all_annotations = Annotation.objects.filter(task=task, project=task.project)
    task_reviewed = True  # If passes all validations it will be reviewed
    for annotation in all_annotations:
        if not get_review(annotation):
            task_reviewed = False
            break
    if task_reviewed:
        task.review_status = Review_status.reviewed
        task.save()


@receiver(pre_save, sender=Annotation)
def make_annotation_unreviewed_pre_save(sender, instance, **kwargs):

    """
    If annotation result updated, make status unreviewed so reviewer can review the new annotaion.
    """

    try:
        annotation = Annotation.objects.get(pk=instance.pk)
    except Annotation.DoesNotExist:
        return False

    if not (instance.result == annotation.result):
        instance.review_status = Annotation_status.no_review


@receiver(pre_delete, sender=Comment)
def make_annotation_unreviewed_pre_delete(sender, instance, **kwargs):

    """
    When a comment is deleted, set annotations status to no_review.
    """

    try:
        annotation = instance.annotation
    except Annotation.DoesNotExist:
        return False

    annotation.review_status = Annotation_status.no_review
    annotation.save()


@receiver(post_delete, sender=Comment)
def make_annotation_unreviewed_post_delete(sender, instance, **kwargs):

    """
    If task's annotations are not reviewed make it unreviewed.
    """

    try:
        annotation = instance.annotation
    except Annotation.DoesNotExist:
        return False

    task = instance.annotation.task
    all_annotations = Annotation.objects.filter(task=task, project=task.project)
    task_reviewed = True  # If passes all validations it will be reviewed
    for annotation in all_annotations:
        if not get_review(annotation):
            task_reviewed = False
            break
    if not task_reviewed:
        task.review_status = Review_status.unreviewed
        task.save()


@receiver(pre_delete, sender=Annotation)
def mark_task_unlabeled(sender, instance, **kwargs):

    """
    After deleting an annotation check task and if it has no other annotations, mark it as unlabeled.
    """

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
    Delete task's file from system after delete.
    """

    try:
        task_file = instance.file
    except Task.DoesNotExist:
        return False

    if task_file:
        if os.path.isfile(task_file.path):
            os.remove(task_file.path)
