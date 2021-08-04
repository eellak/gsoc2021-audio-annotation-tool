from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect

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
from tasks.models import Task, Status, Review_status, Annotation
from tasks.forms import TaskForm
from tasks.serializers import TaskSerializer
from .models import Project
from .serializers import ProjectSerializer
from .permissions import UserCanCreateProject
from .forms import ProjectForm
from .helpers import (
    get_projects_of_user,
    get_user,
    get_project,
    get_task,
    get_annotation,
    get_annotation_result,
    get_num_of_tasks,
    project_annotations_count,
    task_annotations_count,
    users_annotated_task,
    get_project_tasks,
    get_project_url,
    filter_tasks,
    add_labels_to_project,
    next_unlabeled_task_id,
    add_tasks_from_compressed_file,
    delete_old_labels,
)



def index(request):
    """Index view"""
    projects_count = 0
    if request.user.is_authenticated:
        projects = get_projects_of_user(request.user)
        projects_count = projects.count()
    else:
        projects = []

    projects_per_page = 8
    paginator = Paginator(projects, projects_per_page) # Show 10 projects per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "projects_count": projects_count,
        "projects_per_page": projects_per_page,
        "list_num_of_pages": range(1, paginator.num_pages+1),
        "projects": projects,
        "user": request.user,
        "tasks_count": get_num_of_tasks(projects),
        "annotations_count": project_annotations_count(projects),
    }

    return render(request, "label_buddy/index.html", context)


@login_required
def project_create_view(request):
    form = ProjectForm()
    user = get_user(request.user.username)

    if not user or (user != request.user) or not user.can_create_projects:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            # add labels to project
            add_labels_to_project(project, form.cleaned_data['new_labels'])
            # user who created project must be in the list of managers, annotators and reviewers
            project.managers.add(user)
            project.annotators.add(user)
            project.reviewers.add(user)
            messages.add_message(request, messages.SUCCESS, "Successfully created project %s." % project.title)
            return HttpResponseRedirect("/")
        else:
            raise forms.ValidationError("Something is wrong")
    else:
        # if user wants to create project, exclude him from annotators, managers and reviewers list
        form.fields['annotators'].queryset = User.objects.exclude(username=user.username)
        form.fields['managers'].queryset = User.objects.exclude(username=user.username)
        form.fields['reviewers'].queryset = User.objects.exclude(username=user.username)
    
    context = {
        "form":form,
    }
    return render(request, "label_buddy/create_project.html", context)

@login_required
def project_edit_view(request, pk):
    
    form = ProjectForm()
    project = get_project(pk)
    user = get_user(request.user.username)

    # check if user is manager of current project
    if not user or (user != request.user) or not project or not user in project.managers.all():
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
        elif not user in project.managers.all():
            messages.add_message(request, messages.ERROR, "You cannot edit project %s." % project.title) 
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            # delete all labels and add only written ones
            delete_old_labels(project)
            # add labels to project
            add_labels_to_project(project, form.cleaned_data['new_labels'])
            # user who created project must be in the list of managers, annotators and reviewers
            project.managers.add(user)
            project.annotators.add(user)
            project.reviewers.add(user)
            messages.add_message(request, messages.SUCCESS, "Successfully edited project %s." % project.title)
            return HttpResponseRedirect("/")
    else:
        # add existing labels as initial values
        labels_names = []
        for lbl in project.labels.all():
            labels_names.append(lbl.name)
        form = ProjectForm(instance=project, initial={'new_labels': ",".join(labels_names)})

        # if user wants to create project, exclude him from annotators, managers and reviewers list
        form.fields['annotators'].queryset = User.objects.exclude(username=user.username)
        form.fields['managers'].queryset = User.objects.exclude(username=user.username)
        form.fields['reviewers'].queryset = User.objects.exclude(username=user.username)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "label_buddy/edit_project.html", context)

@login_required
def project_delete_view(request, pk):
    project = get_project(pk)
    user = get_user(request.user.username)

    # check if user is manager of current project
    if not user or (user != request.user) or not project or not user in project.managers.all():
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
        elif not user in project.managers.all():
            messages.add_message(request, messages.ERROR, "You cannot delete project %s." % project.title)
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
    task = get_task(task_pk)
    project = get_project(pk)
    user = get_user(request.user.username)

    # check if valid url
    if not user or (user != request.user) or not project or not task:
        if project:
            messages.add_message(request, messages.ERROR, "Task does not exist.")
            return HttpResponseRedirect(get_project_url(project.id))
        else:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect("/")

    # check if user in annotators of project
    if user not in project.annotators.all():
        messages.add_message(request, messages.ERROR, "You are not an annotator for project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    if request.method == "POST":
        annotation = get_annotation(task, project, user)
        if annotation:
            annotation.delete()
            messages.add_message(request, messages.SUCCESS, "Successfully deleted annotation.")
        else:
            messages.add_message(request, messages.ERROR, "Something is wrong.")
        return HttpResponseRedirect(get_project_url(project.id) + "/" + str(task.id) + "/annotation")

    context = {
        "task": task,
        "project_id": project.id,
    }
    return render(request, "label_buddy/delete_annotation.html", context)

@login_required
def project_page_view(request, pk):
    # read filter parameters
    labeled = request.GET.get('labeled', '')
    reviewed = request.GET.get('reviewed', '')

    user = request.user
    project = get_project(pk)
    tasks = filter_tasks(project, labeled, reviewed)
    if not user or (user != request.user) or not project:
        if not project:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
        return HttpResponseRedirect("/")

    if request.method == "POST":
        skipped_files = 0
        task_form = TaskForm(request.POST, request.FILES)
        if task_form.is_valid():
            new_task = task_form.save(commit=False)
            file_extension = str(new_task.file)[-4:]
            # if file uploaded is a zip add new tasks
            if file_extension in ['.zip']:
                # unzip file and add as many tasks as the files in the zip/rar file
                skipped_files = add_tasks_from_compressed_file(new_task.file, project)
            else:
                # one file is uploaded
                new_task.original_file_name = request.FILES['file'].name
                new_task.project = project
                new_task.save()
            
            if skipped_files == 0:
                messages.add_message(request, messages.SUCCESS, "Successful import.")
            else:
                messages.add_message(request, messages.ERROR, "%s files were ignored during the import process." % str(skipped_files))
            return HttpResponseRedirect(get_project_url(project.id))

    else:
        task_form = TaskForm()
    
    tasks_per_page = 8
    paginator = Paginator(tasks, tasks_per_page) # Show 15 tasks per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    setattr(request, 'view', 'projects.views.project_page_view')
    context = {
        "page_obj": page_obj,
        "list_num_of_pages": range(1, paginator.num_pages+1),
        "user": user,
        "project": project,
        "tasks_per_page": tasks_per_page,
        "tasks_count_filtered": tasks.count(),
        "tasks_count_no_filter": get_project_tasks(project).count(),
        "tasks": tasks,
        "annotations_count": Annotation.objects.filter(project=project).count(),
        "count_annotations_for_task": task_annotations_count(tasks),
        "users_annotated": users_annotated_task(tasks),
        "task_form": task_form,
        "labeled": Status.labeled,
        "reviewed": Review_status.reviewed,
    }
    return render(request, "label_buddy/project_page.html", context)

@login_required
def annotate_task_view(request, pk, task_pk):
    
    user = get_user(request.user.username)
    project = get_project(pk)
    task = get_task(task_pk)

    # check if valid url
    if not user or (user != request.user) or not project or not task:
        if project:
            messages.add_message(request, messages.ERROR, "Task does not exist.")
            return HttpResponseRedirect(get_project_url(project.id))
        else:
            messages.add_message(request, messages.ERROR, "Project does not exist.")
            return HttpResponseRedirect("/")

    # check if user in annotators of project
    if user not in project.annotators.all():
        messages.add_message(request, messages.ERROR, "You are not an annotator for project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))

    # Check if task belongs to project
    if task.project != project:
        messages.add_message(request, messages.ERROR, "Task does not belong to project %s." % project.title)
        return HttpResponseRedirect(get_project_url(project.id))
    
    labels = project.labels
    if labels.count() == 0:
        messages.add_message(request, messages.ERROR, "Add some labels to project %s in order to annotate." % project.title)
        return HttpResponseRedirect("/projects/" + str(project.id) + "/edit")
    annotation_result = get_annotation_result(task, project, user)
    annotation = get_annotation(task, project, user)
    
    created_at = annotation.created_at if annotation else None
    updated_at = annotation.updated_at if annotation else None

    context = {
        "labels": labels,
        "labels_count": labels.count(),
        "task": task,
        "project": project,
        "next_unlabeled_task_id": next_unlabeled_task_id(task.id, project),
        "annotation": annotation_result,
        "created_at": created_at,
        "updated_at": updated_at,
        "tasks_count_no_filter": get_project_tasks(project).count(),
        "host": request.build_absolute_uri("/"),
    }

    return render(request, "label_buddy/annotation_page.html", context)

#API VIEWS
class ProjectList(APIView):

    #User will be able to Post only if authenticated 
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, UserCanCreateProject,)
    serializer_class = ProjectSerializer
    '''
    List all projects or create a new one
    '''
    #get request
    def get(self, request, format=None):
        if request.user.is_authenticated:
            projects = get_projects_of_user(request.user)
        else:
            projects = Project.objects.all()

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    #post request
    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_201_CREATED)


class ProjectDetail(APIView):

    '''
    Retrieve, update or delete a project instance.
    '''

    #User will be able to Post only if authenticated 
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
    '''
    List all project's tasks
    '''

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, UserCanCreateProject,)
    serializer_class = TaskSerializer

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except PermissionDenied:
            return Response({"detail": "No permissions"}, status=status.HTTP_401_UNAUTHORIZED)
        except Project.DoesNotExist:
            return Response({"detail": "Project does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    #get all projects tasks
    def get(self, request, pk, format=None):
        project = self.get_object(pk)

        if isinstance(project, Response):
            return project

        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)


#root of out API. shows all objects
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'projects': reverse('project-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'tasks': reverse('task-list', request=request, format=format),
    })
