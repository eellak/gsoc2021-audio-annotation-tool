#functions used for views
from django.db.models import Q

from .models import Project

# get projects where user is manager, annotator or reviewer
def get_projects_of_user(user):
    return Project.objects.filter(Q(reviewers__in=[user]) | Q(annotators__in=[user]) | Q(managers__in=[user])).distinct()