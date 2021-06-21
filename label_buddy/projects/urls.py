from django.urls import path
from .views import (
    projects_list,
    edit_project,
)


#API VIEWS
urlpatterns = [
    path('api/v1/projects/', projects_list, name="projects_list"),
    path('api/v1/projects', projects_list),
    path('api/v1/projects/<pk>', edit_project, name="edit_project"),
    #path('snippets/<int:pk>/', views.snippet_detail),
]