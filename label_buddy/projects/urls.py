from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include, url
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r"^$", views.index),
    url(r"^projects/create$", views.project_create_view, name="create_project"),
    url(r"^projects/(?P<pk>\d+)/data$", views.project_page_view, name="project_page"), # to fix
    #API VIEWS
    path('api/v1/projects/', views.ProjectList.as_view(), name="project-list"),
    path('api/v1/projects/<int:pk>/', views.ProjectDetail.as_view(), name="specific_project"),
    path('api/v1/projects/<int:pk>/tasks', views.ProjectTasks.as_view(), name="project-list-tasks"),
    path('api/v1/root', views.api_root, name="api_root"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
