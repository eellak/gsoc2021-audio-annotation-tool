from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
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