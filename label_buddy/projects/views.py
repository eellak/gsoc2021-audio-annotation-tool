import random
from json import dumps, loads

from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import (
    permissions,
    status,
)

from users.models import User
from tasks.forms import TaskForm
from tasks.serializers import TaskSerializer
from .models import Project
from .serializers import ProjectSerializer
from .permissions import UserCanCreateProject
from .forms import ProjectForm
from tasks.models import (
    Task,
    Annotation,
    Comment,
    Annotation_status,
    Status,
    Review_status,
)
from .helpers import (
    get_projects_of_user,
    get_user,
    get_project,
    get_task,
    get_annotation,
    get_annotation_by_id,
    get_annotation_result,
    get_annotation_review,
    is_user_involved,
    if_annotation_reviewed,
    get_num_of_tasks,
    project_annotations_count,
    task_annotations_count,
    users_annotated_task,
    get_project_tasks,
    get_project_url,
    filter_tasks,
    filter_list_annotations,
    fix_tasks_after_edit,
    add_labels_to_project,
    next_unlabeled_task_id,
    add_tasks_from_compressed_file,
    delete_old_labels,
    users_to_string
)

# Global variables
ACCEPTED_UPLOADED_EXTENSIONS = ['.wav', '.mp3', '.mp4', '.zip']


def index(request):

    """
    Index page view.
    """

    projects_count = 0
    if request.user.is_authenticated:
        projects = get_projects_of_user(request.user)
        projects_count = projects.count()
    else:
        projects = []

    projects_per_page = 8
    paginator = Paginator(projects, projects_per_page)  # Show 8 projects per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Return managers email as html printed manager_email <br>.. for each project
    project_managers_strings = {}

    for project in projects:
        project_managers_strings[project.id] = users_to_string(project.managers.all()) if project.managers.count() > 1 else ""

    context = {
        "page_obj": page_obj,
        "project_managers_strings": project_managers_strings,
        "projects_count": projects_count,
        "projects_per_page": projects_per_page,
        "list_num_of_pages": range(1, paginator.num_pages + 1),
        "projects": projects,
        "user": request.user,
        "tasks_count": get_num_of_tasks(projects),
        "annotations_count": project_annotations_count(projects),
    }

    if request.user.is_authenticated:
        return render(request, "label_buddy/index.html", context)
    else:
        return render(request, "label_buddy/welcome_page.html", context)


@login_required
def project_create_view(request):

    """
    Project create view for creating projects. Only user who have can_create_projects = True can access
    this page.
    """

    form = ProjectForm()
    user = get_user(request.user.username)

    if not user or (user != request.user) or not user.can_create_projects:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            # Add labels to project
            add_labels_to_project(project, form.cleaned_data['new_labels'])
            project.managers.add(user)
            messages.add_message(request, messages.SUCCESS, "Successfully created project %s." % project.title)
            return HttpResponseRedirect("/")
        else:
            raise forms.ValidationError("Something is wrong")
    else:
        # User creating project is manager of the project
        form.fields['managers'].queryset = User.objects.exclude(username=user.username)
        form.fields['annotators'].help_text = "<b>Annotators for the project.</b>"
        form.fields['reviewers'].help_text = "<b>Reviewers for the project.</b>"
        form.fields['managers'].help_text = "<b>Managers for the project. The creator of the project is by default manager.</b>"

    context = {
        "form": form,
    }
    return render(request, "label_buddy/create_project.html", context)


@login_required
def project_edit_view(request, pk):

    """
    Project edit page view for editing a project. Only managers of the project can access this page.
    """

    form = ProjectForm()
    project = get_project(pk)
    user = get_user(request.user.username)

    # Check if user is manager of current project
    if not user or (user != request.user) or not project or user not in project.managers.all():
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
        elif user not in project.managers.all():
            messages.add_message(request, messages.ERROR, "You cannot edit project %s." % project.title)
        return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    if request.method == "POST":
        users_can_see_other_queues_old = project.users_can_see_other_queues
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            new_project = form.save()
            # Delete all labels and add only written ones
            delete_old_labels(new_project)
            # Add labels to project
            add_labels_to_project(new_project, form.cleaned_data['new_labels'])
            project.managers.add(user)
            users_can_see_other_queues_new = new_project.users_can_see_other_queues
            # Function to fix tasks depending on changes. If user changed the users_can_see_other_queues value
            # or if he/she remove an annotator
            fix_tasks_after_edit(users_can_see_other_queues_old, users_can_see_other_queues_new, new_project, user)

            # Check if tasks ok
            # Assert check_tasks_after_edit(new_project) == True, 'Tasks are not ok'

            messages.add_message(request, messages.SUCCESS, "Successfully edited project %s." % new_project.title)
            return HttpResponseRedirect("/")
    else:
        # Add existing labels as initial values
        labels_names = []
        for lbl in project.labels.all():
            labels_names.append(lbl.name)
        form = ProjectForm(instance=project, initial={'new_labels': ",".join(labels_names)})

        form.fields['annotators'].help_text = "<b>Annotators for the project.</b>"
        form.fields['reviewers'].help_text = "<b>Reviewers for the project.</b>"
        form.fields['managers'].help_text = "<b>Managers for the project.</b>"

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "label_buddy/edit_project.html", context)


@login_required
def project_delete_view(request, pk):

    """
    Project delete page view. The manager can delete a project.
    """

    project = get_project(pk)
    user = get_user(request.user.username)

    # If user is manager of current project
    if not user or (user != request.user) or not project or user not in project.managers.all():
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
        elif user not in project.managers.all():
            messages.add_message(request, messages.ERROR, "You cannot delete project %s." % project.title)
        return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    if request.method == "POST":
        project_title = project.title
        project.delete()
        messages.add_message(request, messages.SUCCESS, "Successfully deleted project %s." % project_title)
        return HttpResponseRedirect("/")

    context = {
        "project": project,
    }
    return render(request, "label_buddy/delete_project.html", context)


@login_required
def annotation_delete_view(request, pk, task_pk):

    """
    Annotation delete page view for deleting annotations.
    """

    task = get_task(task_pk)
    project = get_project(pk)
    user = get_user(request.user.username)

    # Check if valid url
    if not user or (user != request.user) or not project or not task:
        if not user or (user != request.user):
            messages.add_message(request, messages.ERROR, "Error")
            return HttpResponseRedirect('/')
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect('/')
        if not task:
            if is_user_involved(user, project):
                messages.add_message(request, messages.ERROR, "Task does not exist.")
                return HttpResponseRedirect(get_project_url(project.id))
            else:
                messages.add_message(request, messages.ERROR, "You are not an annotator for project %s." % project.title)
                return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    # Check if user in annotators of project
    if user not in project.annotators.all():
        messages.add_message(request, messages.ERROR, "You are not an annotator for project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    annotation = get_annotation(task, project, user)
    if not annotation:
        messages.add_message(request, messages.ERROR, "No annotation to delete.")
        return HttpResponseRedirect(get_project_url(project.id) + "/" + str(task.id) + "/annotation")

    if request.method == "POST":
        if annotation:
            annotation.delete()
            messages.add_message(request, messages.SUCCESS, "Successfully deleted annotation.")
        else:
            messages.add_message(request, messages.ERROR, "Something is wrong.")
        return HttpResponseRedirect(get_project_url(project.id) + "/" + str(task.id) + "/annotation")

    context = {
        "task": task,
        "project": project,
    }
    return render(request, "label_buddy/delete_annotation.html", context)


@login_required
def task_delete_view(request, pk, task_pk):

    """
    Task delete page view. Managers can delete uploaded tasks (audio files).
    """

    task = get_task(task_pk)
    project = get_project(pk)
    user = get_user(request.user.username)

    # Check if valid url
    if not user or (user != request.user) or not project or not task:
        if not user or (user != request.user):
            messages.add_message(request, messages.ERROR, "Error")
            return HttpResponseRedirect('/')
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect('/')
        if not task:
            if is_user_involved(user, project):
                messages.add_message(request, messages.ERROR, "Task does not exist.")
                return HttpResponseRedirect(get_project_url(project.id))
            else:
                messages.add_message(request, messages.ERROR, "You are not an annotator for project %s." % project.title)
                return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    # Check if user in magaers of project
    if user not in project.managers.all():
        messages.add_message(request, messages.ERROR, "You are not a manager for the project")
        return HttpResponseRedirect("/")

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    if request.method == "POST":
        task.delete()
        messages.add_message(request, messages.SUCCESS, "Successfully deleted task.")
        return HttpResponseRedirect(get_project_url(project.id))

    context = {
        "task": task,
        "project": project,
    }
    return render(request, "label_buddy/delete_task.html", context)


@login_required
def project_page_view(request, pk):

    """
    Project page view. A page where users can see tasks and information about them. Only tasks for
    the specific project are shown.
    """

    # Read filter parameters
    labeled = request.GET.get('labeled', '')
    reviewed = request.GET.get('reviewed', '')

    user = get_user(request.user.username)
    project = get_project(pk)
    if not user or (user != request.user) or not project:
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
        return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    # If project.users_can_see_other_queues is false,
    # only tasks assigned to logged in user are returned
    # If user is a reviewer all tasks are returned but he/she can annotate
    # only assigned
    tasks, assigned_tasks_count = filter_tasks(user, project, labeled, reviewed)

    if request.method == "POST":
        skipped_files = 0
        task_form = TaskForm(request.POST, request.FILES)
        if task_form.is_valid():
            new_task = task_form.save(commit=False)
            # Check if filed uploaded
            if not new_task.file:
                messages.add_message(request, messages.ERROR, "Please upload a file.")
                response = {'url': get_project_url(project.id)}
                return HttpResponse(dumps(response), status=status.HTTP_400_BAD_REQUEST)
            file_extension = str(new_task.file)[-4:]

            # Check if extension is accepted
            if file_extension not in ACCEPTED_UPLOADED_EXTENSIONS:
                messages.add_message(request, messages.ERROR, "%s is not an accepted extension." % file_extension)
                response = {'url': get_project_url(project.id)}
                return HttpResponse(dumps(response), status=status.HTTP_400_BAD_REQUEST)

            # If file uploaded is a zip add new tasks
            if file_extension in [".zip", ".rar"]:
                # Unzip file and add as many tasks as the files in the zip/rar file
                skipped_files = add_tasks_from_compressed_file(new_task.file, project, file_extension)

                """
                Random users assigned in function add_tasks_from_compressed_file.
                """

            else:
                # One file is uploaded
                new_task.original_file_name = request.FILES['file'].name
                new_task.project = project
                new_task.save()

                """
                If project users_can_see_other_queues is false, assign task to a random annotator.
                """

                if not project.users_can_see_other_queues:
                    random_annotator = random.choice(list(project.annotators.all()))
                    new_task.assigned_to.add(random_annotator)

            if skipped_files == 0:
                messages.add_message(request, messages.SUCCESS, "Successful import.")
            else:
                messages.add_message(request, messages.ERROR, "%s files were ignored during the import process." % str(skipped_files))
            response = {'url': get_project_url(project.id)}
            return HttpResponse(dumps(response), status=status.HTTP_200_OK)

    else:
        task_form = TaskForm()

    tasks_per_page = 8
    paginator = Paginator(tasks, tasks_per_page)  # Show 8 tasks per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    setattr(request, 'view', 'projects.views.project_page_view')

    # If user has annotated task
    annotated_tasks = {}
    annotated_tasks_status = {}
    for task in tasks:
        user_annotation = get_annotation(task, project, user)
        annotated_tasks[task.id] = user_annotation
        annotated_tasks_status[task.id] = user_annotation.review_status.name if user_annotation else None

    task_annotators, annotations_count = users_annotated_task(tasks)
    context = {
        "page_obj": page_obj,
        "list_num_of_pages": range(1, paginator.num_pages + 1),
        "user": user,
        "project": project,
        "tasks_per_page": tasks_per_page,
        "tasks_count_filtered": len(tasks),
        "tasks_count_no_filter": get_project_tasks(project).count(),
        "tasks": tasks,
        "count_annotations_for_task": task_annotations_count(tasks),
        "string_annotators": task_annotators,
        "annotations_count": annotations_count,
        "task_form": task_form,
        "labeled": Status.labeled,
        "reviewed": Review_status.reviewed,
        "annotated_tasks": annotated_tasks,
        "annotated_tasks_status": annotated_tasks_status,
        "assigned_tasks_count": assigned_tasks_count
    }
    return render(request, "label_buddy/project_page.html", context)


@login_required
def annotate_task_view(request, pk, task_pk):

    """
    Annotate tasks page view. Only annotators of a project can access this page. They can annotate
    tasks, update annotations and delete them.
    """

    user = get_user(request.user.username)
    project = get_project(pk)
    task = get_task(task_pk)

    if not user or (user != request.user) or not project or not task:
        if not user or (user != request.user):
            messages.add_message(request, messages.ERROR, "Error")
            return HttpResponseRedirect('/')
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect('/')
        if not task:
            if is_user_involved(user, project):
                messages.add_message(request, messages.ERROR, "Task does not exist.")
                return HttpResponseRedirect(get_project_url(project.id))
            else:
                messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
                return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    # Check if user in annotators of project
    if user not in project.annotators.all():
        messages.add_message(request, messages.ERROR, "You are not an annotator for project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    labels = project.labels
    if labels.count() == 0:
        if user in project.managers.all():
            messages.add_message(request, messages.ERROR, "Add some labels to project %s in order to annotate." % project.title)
            return HttpResponseRedirect("/projects/" + str(project.id) + "/edit")
        else:
            messages.add_message(request, messages.ERROR, "Labels must be added for project %s by a manager in order to enable annotation." % project.title)
            return HttpResponseRedirect("/")

    # Check if task is assigned to current user
    if not project.users_can_see_other_queues:
        if task.assigned_to.exists() and user not in task.assigned_to.all():
            messages.add_message(request, messages.ERROR, "Task %s is not assigned to you." % str(task.id))
            return HttpResponseRedirect(get_project_url(project.id))

    annotation_result = get_annotation_result(task, project, user)
    annotation = get_annotation(task, project, user)

    created_at = annotation.created_at if annotation else None
    updated_at = annotation.updated_at if annotation else None
    annotation_status = annotation.review_status if annotation else None

    reviewer, comment, review_created_at, review_updated_at = if_annotation_reviewed(annotation)
    context = {
        "labels": labels,
        "labels_count": labels.count(),
        "task": task,
        "project": project,
        "next_unlabeled_task_id": next_unlabeled_task_id(task.id, project),
        "annotation_result": annotation_result,
        "created_at": created_at,
        "updated_at": updated_at,
        "annotation_status": annotation_status,
        "status_approved": Annotation_status.approved,
        "status_rejected": Annotation_status.rejected,
        "status_no_review": Annotation_status.no_review,
        "reviewer": reviewer,
        "comment": comment,
        "review_created_at": review_created_at,
        "review_updated_at": review_updated_at,
        "tasks_count_no_filter": get_project_tasks(project).count(),
    }

    return render(request, "label_buddy/annotation_page.html", context)


@login_required
def list_annotations_for_task_view(request, pk, task_pk):

    """
    List annotations for a task page view. In this page, reviewers can see all annotations done
    for a specific task and review any them, approving or rejecting them.
    """

    user = get_user(request.user.username)
    project = get_project(pk)
    task = get_task(task_pk)

    if not user or (user != request.user) or not project or not task:
        if not user or (user != request.user):
            messages.add_message(request, messages.ERROR, "Error")
            return HttpResponseRedirect('/')
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect('/')
        if not task:
            if is_user_involved(user, project):
                messages.add_message(request, messages.ERROR, "Task does not exist.")
                return HttpResponseRedirect(get_project_url(project.id))
            else:
                messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
                return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    # Check if user in managers or reviewers of project
    if user not in project.reviewers.all():
        messages.add_message(request, messages.ERROR, "You are not a reviewer for project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Get all annotations
    task_annotations = Annotation.objects.filter(Q(task=task) & Q(project=project))

    # Exclude annotations that are reviewed but not from the current user
    to_exclude_ids = []
    for annotation in task_annotations:
        user_reviewed, _, _, _ = if_annotation_reviewed(annotation)
        if user_reviewed and user_reviewed != user:
            to_exclude_ids.append(annotation.id)

    task_annotations = task_annotations.exclude(id__in=to_exclude_ids)
    if task_annotations.count() == 0:
        messages.add_message(request, messages.WARNING, "No annotations to review.")
        return HttpResponseRedirect(get_project_url(project.id))

    annotations_reviewed_by_user = {}
    for annotation in task_annotations:
        annotations_reviewed_by_user[annotation.id] = get_annotation_review(user, annotation)

    # Read filter parameters
    approved_filter = request.GET.get('approved', '')
    rejected_filter = request.GET.get('rejected', '')
    unreviewed_filter = request.GET.get('unreviewed', '')

    # Only if filters are set call function
    if approved_filter or rejected_filter or unreviewed_filter:
        task_annotations = filter_list_annotations(task_annotations, approved_filter, rejected_filter, unreviewed_filter)

    annotations_per_page = 8
    paginator = Paginator(task_annotations, annotations_per_page)  # Show 8 tasks per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # If 2 or more annotations go to list annotations page
    context = {
        "user": user,
        "page_obj": page_obj,
        "list_num_of_pages": range(1, paginator.num_pages + 1),
        "task": task,
        "project": project,
        "annotations": task_annotations,
        "annotations_count": task_annotations.count(),
        "annotations_per_page": annotations_per_page,
        "approved": Annotation_status.approved,
        "rejected": Annotation_status.rejected,
        "annotations_reviewed_by_user": annotations_reviewed_by_user,
    }
    return render(request, "label_buddy/list_annotations.html", context)


@login_required
def review_annotation_view(request, pk, task_pk, annotation_pk):

    """
    Review annotation page. Reviewers can review annotations by writing a comment and approving or rejecting them.
    """

    user = get_user(request.user.username)
    project = get_project(pk)
    task = get_task(task_pk)
    to_review_annotation = get_annotation_by_id(annotation_pk)

    if not user or (user != request.user) or not project or not task or not to_review_annotation:
        if not user or (user != request.user):
            messages.add_message(request, messages.ERROR, "Error")
            return HttpResponseRedirect('/')
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect('/')
        if not task:
            if is_user_involved(user, project):
                messages.add_message(request, messages.ERROR, "Task does not exist.")
                return HttpResponseRedirect(get_project_url(project.id))
            else:
                messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
                return HttpResponseRedirect("/")

        if not to_review_annotation:
            if is_user_involved(user, project):
                messages.add_message(request, messages.ERROR, "Annotation does not exist.")
                return HttpResponseRedirect(get_project_url(project.id))
            else:
                messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
                return HttpResponseRedirect("/")

    # Check if user involved to project
    if not is_user_involved(user, project):
        messages.add_message(request, messages.ERROR, "You are not involved to requested project.")
        return HttpResponseRedirect("/")

    # Check if user in managers or reviewers of project
    if user not in project.reviewers.all():
        messages.add_message(request, messages.ERROR, "You are not a reviewer for project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if annotation belongs to project
    if to_review_annotation.project != project:
        messages.add_message(request, messages.ERROR, "Annotation requested does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id) + "/" + str(task.id) + "/list_annotations")

    # Check if annotation belongs to task
    if to_review_annotation.project != project:
        messages.add_message(request, messages.ERROR, "Annotation requested does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id) + "/" + str(task.id) + "/list_annotations")

    # Assert that annotation is either reviewed by user or is unreviewed
    annotation_reviewer, _, _, _ = if_annotation_reviewed(to_review_annotation)
    if annotation_reviewer and annotation_reviewer != user:
        messages.add_message(request, messages.WARNING, "This annotation is being reviewed by another user.")
        return HttpResponseRedirect(get_project_url(project.id) + "/" + str(task.id) + "/list_annotations")

    if request.method == "POST":
        data = loads(request.body)
        action = data['value']

        # If annotation unreviewed create reviewapproved set annotation's status to approved
        if action in ["APPROVE", "REJECT"]:
            annotation_status = ""
            if action == "APPROVE":
                annotation_status = Annotation_status.approved
            else:
                annotation_status = Annotation_status.rejected

            user_review = get_annotation_review(user, to_review_annotation)
            to_review_annotation.review_status = annotation_status  # Set annotation's status either way
            to_review_annotation.save()
            # If there is no a review yet, create one else update
            if user_review:
                user_review.comment = data['comment']
                user_review.updated_at = timezone.now()
                user_review.save()
            else:
                Comment.objects.create(
                    reviewed_by=user,
                    annotation=to_review_annotation,
                    comment=data['comment']
                )
            if data['comment'] == "":
                messages.add_message(request, messages.WARNING, "You submitted a review with an empty comment.")
            else:
                if user_review:
                    messages.add_message(request, messages.SUCCESS, "Review updated successfully.")
                else:
                    messages.add_message(request, messages.SUCCESS, "Review created successfully.")
            return HttpResponse(status=status.HTTP_200_OK)
        elif action == "DELETE":
            user_review = get_annotation_review(user, to_review_annotation)
            if user_review:
                user_review.delete()
                messages.add_message(request, messages.SUCCESS, "Review deleted successfully. You can review the annotation again as long as it's still unreviewed.")
                return HttpResponse(status=status.HTTP_200_OK)
            else:
                messages.add_message(request, messages.ERROR, "No review to delete.")
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        else:
            messages.add_message(request, messages.ERROR, "Something is wrong.")
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    reviewer, comment, review_created_at, review_updated_at = if_annotation_reviewed(to_review_annotation)
    # Get review of annotation, assert that if exists user == current user
    if reviewer:
        assert reviewer == user
    context = {
        "reviewer": reviewer,
        "review_created_at": review_created_at,
        "review_updated_at": review_updated_at,
        "comment": comment,
        "status_approved": Annotation_status.approved,
        "status_rejected": Annotation_status.rejected,
        "labels": project.labels,
        "labels_count": project.labels.count(),
        "annotation": to_review_annotation,
        "annotation_result": dumps(to_review_annotation.result),
        "project": project,
        "task": task,
    }
    return render(request, "label_buddy/review_page.html", context)


# API VIEWS
class ProjectList(APIView):
    # User will be able to Post only if authenticated
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, UserCanCreateProject,)
    serializer_class = ProjectSerializer

    """
    List all projects or create a new one.
    """

    # Get request
    def get(self, request, format=None):
        if request.user.is_authenticated:
            projects = get_projects_of_user(request.user)
        else:
            projects = Project.objects.all()

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    # Post request
    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_201_CREATED)


class ProjectDetail(APIView):

    """
    Retrieve, update or delete a project instance.
    """

    # User will be able to Post only if authenticated
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, UserCanCreateProject,)
    serializer_class = ProjectSerializer

    def get_object(self, pk):

        try:
            return Project.objects.get(pk=pk)
        except PermissionDenied:
            return Response({"detail": "No permissions"}, status=status.HTTP_401_UNAUTHORIZED)
        except Project.DoesNotExist:
            return Response({"detail": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project)
        if isinstance(project, Response):
            return project

        return Response(serializer.data)

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectTasks(APIView):

    """
    List all project's tasks.
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, UserCanCreateProject,)
    serializer_class = TaskSerializer

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except PermissionDenied:
            return Response({"detail": "No permissions"}, status=status.HTTP_401_UNAUTHORIZED)
        except Project.DoesNotExist:
            return Response({"detail": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    # Get all projects tasks
    def get(self, request, pk, format=None):
        project = self.get_object(pk)

        if isinstance(project, Response):
            return project

        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)


# Root of out API. shows all objects
@api_view(['GET'])
def api_root(request, format=None):

    """
    API root view. All api endpoints are listed and can be accessed.
    """

    return Response({
        'projects': reverse('project-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'tasks': reverse('task-list', request=request, format=format),
    })
