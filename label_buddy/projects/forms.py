from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):

    title = forms.CharField(label='', widget=forms.TextInput(attrs={"placeholder": "Title"}))
    description = forms.CharField(required=False, widget=forms.Textarea(
        attrs = {
            "placeholder": "Description",
            "rows": 5,
        }
    ))
    instructions = forms.CharField(required=False, widget=forms.Textarea(
        attrs = {
            "placeholder": "Description",
            "rows": 5,
        }
    ))
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "instructions",
            "logo",
            "users_can_see_other_queues",
            "labels",
            "reviewers",
            "annotators",
        ]
