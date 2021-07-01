from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse
from rest_framework import (
    permissions,
    status,
)



from .models import User
from .serializers import UserSerializer
# Create your views here.


#API VIEWS
class UserList(APIView):

    #User will be able to Post only if authenticated 
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer
    '''
    List all users or create a new one
    '''
    #get request
    def get(self, request, format=None):
        
        users = User.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    #post request
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserDetail(APIView):

    '''
    Retrieve, update or delete a user instance.
    '''

    #User will be able to Post only if authenticated 
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer

    def get_object(self, pk):

        try:
            return User.objects.get(pk=pk)
        except PermissionDenied:
            return Response({"detail": "No permissions"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        if isinstance(user, Response):
            return user

        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)