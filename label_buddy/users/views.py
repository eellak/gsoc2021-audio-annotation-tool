from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework import (
    permissions,
    status,
)


from .models import User
from .serializers import UserSerializer
from .forms import UserForm
# Create your views here


def get_user(username):

    """
    Get user by username.
    """

    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None


@login_required
def edit_profile(request, username):

    """
    View for user edit profile. The user can update his/her information.
    """

    context = {}
    user = get_user(username)
    if not user or (user != request.user):
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            new_user = form.save(commit=False)
            # Cannot change email
            new_user.email = user.email
            new_user.save()
            messages.add_message(request, messages.SUCCESS, "Successfully edited profile.")
            return HttpResponseRedirect("/")
    else:
        form = UserForm(instance=user)
        form.fields['email'].widget.attrs['readonly'] = True

    context["form"] = form
    return render(request, "label_buddy/user_edit_profile.html", context)


# API VIEWS
class UserList(APIView):

    """
    List all users or create a new one.
    """

    # User will be able to Post only if authenticated
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer

    # Get request
    def get(self, request, format=None):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # Post request
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):

    """
    Retrieve, update or delete a user instance.
    """

    # User will be able to Post only if authenticated
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer

    def get_object(self, pk):

        try:
            return User.objects.get(pk=pk)
        except PermissionDenied:
            return Response({"detail": "No permissions"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        if isinstance(user, Response):
            return user

        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
