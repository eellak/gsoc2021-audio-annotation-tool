from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):

    title = forms.CharField(label='', widget=forms.TextInput(attrs={"placeholder": "Title"}))
    
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "logo",
            "users_can_see_other_queues",
            "labels",
            "reviewers",
            "annotators",
            "managers",
            "project_type",
        ]









# title = models.CharField(max_length=256, blank=False, null=False, default='', help_text='Project title')

#     description = models.TextField(blank=True, null=True, default='', help_text='Project description')
#     instructions = models.TextField(blank=True, null=True, default='', help_text='Project instructions')
#     logo = models.ImageField(blank=True, help_text='Project logo')
#     created_at = models.DateTimeField(auto_now=True, help_text='Date and time of project creation')

#     users_can_see_other_queues = models.BooleanField(default=False, help_text='If true, users can see which tasks are assinged to other users for this specific project')

#     labels = models.ManyToManyField(Label, blank=False, help_text='Labels used by annotators to annotate')
#     reviewers = models.ManyToManyField(User, blank=True, related_name='project_reviewer', help_text='Reviewers who will review annotations')
#     annotators = models.ManyToManyField(User, blank=True, related_name='project_annotator', help_text='Annotators for the project')
#     managers = models.ManyToManyField(User, blank=True, related_name='project_manager', help_text='Managers for the project')

#     project_type = EnumChoiceField(Project_type, default=Project_type.audio, help_text='Specify the type of the annotation (Audio, image or Video)')