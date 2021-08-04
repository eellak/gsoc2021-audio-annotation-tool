#functions used for views
import random
from zipfile import ZipFile
from json import dumps

from django.core.files import File
from django.db.models import Q
from django.template.defaulttags import register

from .models import Project, Label
from users.models import User
from tasks.forms import TaskForm
from tasks.models import (
    Task,
    Annotation,
    Status,
    Review_status,
)

# global variables
ACCEPTED_EXTENSIONS = ['.wav', '.mp3', '.mp4',]

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

# get annotation updated_at and result by task, project and user
def get_annotation_result(task, project, user):
    try:
        annotation = Annotation.objects.get(task=task, project=project, user=user)
        return dumps(annotation.result)
    except Annotation.DoesNotExist:
        return dumps({})


# get label by name
def get_label(name):
    try:
        label = Label.objects.get(pk=name)
        return label
    except Label.DoesNotExist:
        return None

def get_label_by_color(color):
    try:
        label = Label.objects.get(color=color)
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
    labels_of_project = project.labels.all()
    for new in new_labels:
        name = new.strip()
        label = get_label(name)
        if not label:
            color = random_color()
            # make sure the color does not already exist
            while get_label_by_color(color):
                color = random_color()
            if name != "":
                label = Label.objects.create(name=name, color=color)
        if label and label not in labels_of_project:
            project.labels.add(label)

# used for edit project
def delete_old_labels(project):
    for label in project.labels.all():
        project.labels.remove(label)



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


# unzip file and add tasks
def add_tasks_from_compressed_file(compressed_file, project):
    archive = ZipFile(compressed_file, 'r')
    files_names = archive.namelist()

    skipped_files = 0
    for filename in files_names:
        new_file = archive.open(filename, "r")
        # for every file that has an extension in [.wav, .mp3, .mp4] create a task
        if filename[-4:] in ACCEPTED_EXTENSIONS:
            # create task
            new_task = Task.objects.create(project=project, original_file_name=filename)
            new_task.file.save(filename, File(new_file))
        else:
            skipped_files += 1
    return skipped_files


# functions for annotation page

# return next unlabeled task
def next_unlabeled_task_id(current_task_id, project):
    ordered_tasks = Task.objects.filter(project=project).order_by("-id")
    min_id = ordered_tasks.reverse()[0].id
    max_id = ordered_tasks[0].id

    for task_id in range(min_id, max_id+1):
        task = get_task(task_id)
        if task and task.file and task_id != current_task_id and task.status == Status.unlabeled:
            return task_id
    return -1

# in order to access dictionary in templates as dict[key]
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# calculate correct id for table in project page
@register.simple_tag
def get_table_id(current_page, objects_per_page, loop_counter):
    return ((current_page - 1)*objects_per_page) + loop_counter