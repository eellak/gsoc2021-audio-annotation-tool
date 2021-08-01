from django import forms

from .models import Task

class TaskForm(forms.ModelForm):

    file = forms.FileField(label='', widget=forms.FileInput(attrs={"id": "import-file", "onchange": "checkExtension(this)"}))
    class Meta:
        model = Task
        fields = [
            "file",
        ]
