from django.shortcuts import render

from .models import Project
from .serializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView



class ProjectList(APIView):

    serializer_class = ProjectSerializer
    '''
    LIst all projects or create a new one
    '''
    #get request
    def get(self, request, format=None):
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


# from rest_framework import viewsets
# from rest_framework.decorators import action
# class ProjectViewSet(viewsets.ModelViewSet):
#     """
#     This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
#     """
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]