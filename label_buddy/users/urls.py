from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    
    #API VIEWS
    path('api/v1/users/', views.UserList.as_view(), name="user-list"),
]

urlpatterns = format_suffix_patterns(urlpatterns)