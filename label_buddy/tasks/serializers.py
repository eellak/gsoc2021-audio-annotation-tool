from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "project",
            "file",
            "url",
            "extra",
            "status",
            "review_status",
            "assigned_to",
        ]