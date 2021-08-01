from django import forms

from .models import Project, Label

class ProjectForm(forms.ModelForm):

    title = forms.CharField(label='Tile', required=False, widget=forms.TextInput(attrs={"placeholder": "Title"}))
    description = forms.CharField(required=False, widget=forms.Textarea(
        attrs = {
            "placeholder": "Description",
            "rows": 4,
        }
    ))
    instructions = forms.CharField(required=False, widget=forms.Textarea(
        attrs = {
            "placeholder": "Instructions",
            "rows": 4,
        }
    ))
    new_labels = forms.CharField(label="Labels", required=False, widget=forms.TextInput(
        attrs = {
            "placeholder": "A comma separated list of new labels",
            "id": "new_labels",
        }
    ))
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "instructions",
            "logo",
            "new_labels",
            "users_can_see_other_queues",
            "annotators",
            "managers",
            "reviewers",
        ]
