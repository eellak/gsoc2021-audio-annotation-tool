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
from .methods import get_projects_of_user
from .forms import ProjectForm
from users.models import User

def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None

@login_required
def index(request):
    """Index view"""
    if request.user.is_authenticated:
        projects = get_projects_of_user(request.user)
    else:
        projects = []

    context = {
        "projects": projects,
        "user": request.user,
    }

    return render(request, "label_buddy/index.html", context)


@login_required
def project_create_view(request, username):
    user = get_user(username)
    form = ProjectForm()
    if not user or (user != request.user):
        return HttpResponseRedirect("/")
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            # user who created project must be in the list of managers
            project.managers.add(user)
            return HttpResponseRedirect("/")
        else:
            print(form.errors)
    context = {
        "form":form,
    }
    return render(request, "label_buddy/create_project.html", context)




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
