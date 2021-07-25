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


from tasks.models import Task
from tasks.serializers import TaskSerializer
from .models import Project
from .serializers import ProjectSerializer
from .permissions import UserCanCreateProject
from .forms import ProjectForm
from .helpers import (
    get_projects_of_user,
    get_user,
    get_project,
    get_num_of_tasks,
    project_annotations_count,
    task_annotations_count,
    get_project_tasks,
    users_annotated_task,
    get_project_url,
)



def index(request):
    """Index view"""
    if request.user.is_authenticated:
        projects = get_projects_of_user(request.user)
    else:
        projects = []

    context = {
        "projects": projects,
        "user": request.user,
        "tasks_count": get_num_of_tasks(projects),
        "annotations_count": project_annotations_count(projects),
    }

    return render(request, "label_buddy/index.html", context)


@login_required
def project_create_view(request):
    form = ProjectForm()
    user = request.user

    if not user or (user != request.user) or not user.can_create_projects:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            # user who created project must be in the list of managers
            project.managers.add(user)
            return HttpResponseRedirect("/")
        else:
            raise forms.ValidationError("Something is wrong")
    context = {
        "form":form,
    }
    return render(request, "label_buddy/create_project.html", context)

@login_required
def project_edit_view(request, pk):
    project = get_project(pk)
    user = request.user

    # check if user is manager of current project
    if not user or (user != request.user) or not user in project.managers.all():
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            return HttpResponseRedirect(get_project_url(project.id))
    else:
        form = ProjectForm(instance=project)

    context = {
        "project": project,
        "form": form,
    }
    return render(request, "label_buddy/edit_project.html", context)


@login_required
def project_page_view(request, pk):
    user = request.user
    project = get_project(pk)
    tasks = get_project_tasks(project)
    if not user or (user != request.user) or not project:
        return HttpResponseRedirect("/")
    
    context = {
        "user": user,
        "project": project,
        "tasks": tasks,
        "count_annotations_for_task": task_annotations_count(tasks),
        "users_annotated": users_annotated_task(tasks),
    }
    return render(request, "label_buddy/project_page.html", context)


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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
