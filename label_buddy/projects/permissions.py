from rest_framework import permissions


class UserCanCreateProject(permissions.BasePermission):
    '''
    Custom permission to only allow users who can create projects to do so.
    '''

    def has_permission(self, request, view):
        '''
        Allow to post only if user Can create projects
        '''
        #Allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.can_create_projects

    def has_object_permission(self, request, view, obj):
        
        #if user is part of the specific project then return true, else false
        user = request.user
        if (user in obj.reviewers.all()) or (user in obj.annotators.all()) or (user in obj.managers.all()):
            return True 

        return False