#functions used for views
from django.db.models import Q

from .models import Project
from users.models import User

# get projects where user is manager, annotator or reviewer
def get_projects_of_user(user):
    return Project.objects.filter(Q(reviewers__in=[user]) | Q(annotators__in=[user]) | Q(managers__in=[user])).distinct()

# get user by username
def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None

# get projects by id
def get_project(pk):
    try:
        project = Project.objects.get(pk=pk)
        return project
    except Project.DoesNotExist:
        return None