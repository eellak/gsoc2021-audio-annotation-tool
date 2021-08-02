from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
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
from tasks.models import Task, Status, Review_status
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
    get_annotation_info,
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
    # if redirected from login
    from_login = True if request.GET.get('login', '') == 'true' else False
    # if redirected from delete
    from_delete = True if request.GET.get('delete', '') == 'true' else False
    project_deleted = request.GET.get('title', '') if request.GET.get('delete', '') else ""
    # if redirected from create
    project_created = True if request.GET.get('create', '') == 'true' else False
    project_created_title = request.GET.get('title_created', '') if request.GET.get('title_created', '') else ""

    projects_count = 0
    if request.user.is_authenticated:
        projects = get_projects_of_user(request.user)
        projects_count = projects.count()
    else:
        projects = []

    projects_per_page = 10
    paginator = Paginator(projects, projects_per_page) # Show 10 projects per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # send correct message
    message = None
    if request.user.is_authenticated and from_login:
        message = "Successfully singed in as " + request.user.username + "!"
    if from_delete:
        message = "Successful deletion of project " + project_deleted + "!"
    if project_created:
        message = "Successful creation of project " + project_created_title + "!"
    
    context = {
        "message": message,
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

            return HttpResponseRedirect("/?create=true&title_created=" + project.title)
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
    # if redirected for project with no labels
    project_has_no_labels = True if request.GET.get('no_labels', '') == 'true' else False
    form = ProjectForm()
    project = get_project(pk)
    user = get_user(request.user.username)

    # check if user is manager of current project
    if not user or (user != request.user) or not project or not user in project.managers.all():
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
            return HttpResponseRedirect(get_project_url(project.id))
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

    message = None 
    if project_has_no_labels:
        message = "Add some labels to project " + project.title + " in order to annotate!"
    context = {
        "message": message,
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
        return HttpResponseRedirect("/")

    if request.method == "POST":
        project_title = project.title
        project.delete()
        return HttpResponseRedirect("/?delete=true&title=" + project_title)
    
    context = {
        "project": project,
    }
    return render(request, "label_buddy/delete_project.html", context)

@login_required
def project_page_view(request, pk):
    # read filter parameters
    labeled = request.GET.get('labeled', '')
    reviewed = request.GET.get('reviewed', '')

    # skipped files from import
    num_of_skipped_files = int(request.GET.get('skipped', '')) if request.GET.get('skipped', '') else 0

    user = request.user
    project = get_project(pk)
    tasks = filter_tasks(project, labeled, reviewed)
    if not user or (user != request.user) or not project:
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
                new_task.project = project
                new_task.save()
            return HttpResponseRedirect(get_project_url(project.id) + '?skipped=' + str(skipped_files))

    else:
        task_form = TaskForm()
    
    tasks_per_page = 10
    paginator = Paginator(tasks, tasks_per_page) # Show 15 tasks per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "list_num_of_pages": range(1, paginator.num_pages+1),
        "user": user,
        "project": project,
        "tasks_per_page": tasks_per_page,
        "tasks_count_filtered": tasks.count(),
        "tasks_count_no_filter": get_project_tasks(project).count(),
        "tasks": tasks,
        "count_annotations_for_task": task_annotations_count(tasks),
        "users_annotated": users_annotated_task(tasks),
        "task_form": task_form,
        "labeled": Status.labeled,
        "reviewed": Review_status.reviewed,
        "num_of_skipped_files": num_of_skipped_files,
        "from_import": request.GET.get('skipped', ''),
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
            return HttpResponseRedirect(get_project_url(project.id))
        else:
            return HttpResponseRedirect("/")

    # check if user in annotators of project and if task belongs to project
    if user not in project.annotators.all() or task.project != project:
        return HttpResponseRedirect(get_project_url(project.id))


    labels = project.labels
    if labels.count() == 0:
        return HttpResponseRedirect("/projects/" + str(project.id) + "/edit?no_labels=true")

    context = {
        "labels": labels,
        "labels_count": labels.count(),
        "task": task,
        "project": project,
        "next_unlabeled_task_id": next_unlabeled_task_id(task.id, project),
        "annotation": get_annotation_info(task, project, user),
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
