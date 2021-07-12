#functions used for views
from django.db.models import Q
from django.template.defaulttags import register

from .models import Project
from users.models import User
from tasks.models import Task, Annotation

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

# return a dictionary id: number of tasks for every project
def get_num_of_tasks(projects):
    context = {}

    for project in projects:
        context[project.id] = Task.objects.filter(project=project).count()
    return context

# return a dictionary id: number of annotations for every project
def get_num_of_annotations(projects):
    context = {}

    for project in projects:
        context[project.id] = Annotation.objects.filter(project=project).count()
    return context


# in order to access dictionary in templates as dict[key]
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)