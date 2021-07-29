#functions used for views
import random
from django.db.models import Q
from django.template.defaulttags import register

from .models import Project, Label
from users.models import User
from tasks.models import (
    Task,
    Annotation,
    Status,
    Review_status,
)

# Functions

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

# get task by id
def get_task(pk):
    try:
        task = Task.objects.get(pk=pk)
        return task
    except Task.DoesNotExist:
        return None

# get label by name
def get_label(name):
    try:
        label = Label.objects.get(pk=name)
        return label
    except Label.DoesNotExist:
        return None

# get random color
def random_color():
    random_number = random.randint(0,16777215)
    hex_number = str(hex(random_number))
    return '#'+ hex_number[2:]
# functions for index page

# return a dictionary id: number of tasks for every project
def get_num_of_tasks(projects):
    context = {}

    for project in projects:
        context[project.id] = Task.objects.filter(project=project).count()
    return context

# return a dictionary id: number of annotations for every project
def project_annotations_count(projects):
    context = {}

    for project in projects:
        context[project.id] = Annotation.objects.filter(project=project).count()
    return context


# get all tasks of a project and return them
def get_project_tasks(project):
    return Task.objects.filter(project=project)

# create labels that dont exist and add all of them to the project
def add_labels_to_project(project, labels):
    new_labels = labels.split(',')

    for new in new_labels:
        name = new.strip()
        label = get_label(name)
        if not label:
            color = random_color()
            label = Label.objects.create(name=name, color=color)
        if label not in project.labels.all():
            project.labels.add(label)





# functions for project page

# return boolean of string. If it returns noe then the string is not boolean (true or false)
def str_to_bool(string):
    string = string.lower()
    if string == "true":
        return True
    elif string == "false":
        return False
    return None


# return filtered tasks
def filter_tasks(project, labeled, reviewed):

    bool_labeled = str_to_bool(labeled)
    bool_reviewed = str_to_bool(reviewed)
    tasks = get_project_tasks(project)

    # set status and review_status to correct values
    if bool_labeled is not None:
        if bool_labeled:
            status = Status.labeled
        else:
            status = Status.unlabeled
    
    if bool_reviewed is not None:
        if bool_reviewed:
            review_status = Review_status.reviewed
        else:
            review_status = Review_status.unreviewed
    
    # if no filters applied
    if bool_labeled is None and bool_reviewed is None:
        return tasks

    # if both filters applied
    if bool_labeled is not None and bool_reviewed is not None:
        return tasks.filter(status=status, review_status=review_status)
    
    # if status filter is applied
    if bool_labeled is not None:
        return tasks.filter(status=status)

    # if review filter is applied
    if bool_reviewed is not None:
        return tasks.filter(review_status=review_status)


# return project's page url
def get_project_url(pk):
    return "/projects/" + str(pk) + "/tasks"

# return dictionary dict[id] = number of annotations for task, for all tasks
def task_annotations_count(tasks):
    context = {}
    for task in tasks:
        context[task.id] = Annotation.objects.filter(task=task).count()
    return context

# return dictionary dict[task.id] = [user1, userxx, ...] with all users annotated this task
def users_annotated_task(tasks):
    context = {}
    for task in tasks:
        query = Annotation.objects.filter(task=task)
        annotators = []
        for annotation in query:
            annotators.append(annotation.user)
        context[task.id] = annotators
    return context

# in order to access dictionary in templates as dict[key]
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)