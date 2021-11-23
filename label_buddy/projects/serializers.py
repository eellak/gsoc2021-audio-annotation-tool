from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):

    """
    Serializer for project API endpoint data.
    """

    class Meta:
        model = Project
        read_only_fields = [
            "users_can_see_other_queues",
        ]
        fields = [
            "title",
            "description",
            "instructions",
            "logo",
            "project_type",
            "labels",
            "reviewers",
            "annotators",
            "managers",
        ]
