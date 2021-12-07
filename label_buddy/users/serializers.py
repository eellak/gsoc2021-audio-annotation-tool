from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    """
    Serializer for user API endpoint data.
    """

    class Meta:
        model = User
        fields = [
            "name",
            "username",
            "email",
        ]
