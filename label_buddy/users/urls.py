from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    
    #API VIEWS
    path('api/v1/users/', views.UserList.as_view(), name="user-list"),
    path('api/v1/users/<int:pk>/', views.UserDetail.as_view(), name="specific_user"),
]

urlpatterns = format_suffix_patterns(urlpatterns)