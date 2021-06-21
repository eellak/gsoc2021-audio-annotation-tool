from django.urls import path
from .views import projects_list


#API VIEWS
urlpatterns = [
    path('api/v1/projects/', projects_list, name="projects_list"),
    path('api/v1/projects', projects_list),
    #path('snippets/<int:pk>/', views.snippet_detail),
]