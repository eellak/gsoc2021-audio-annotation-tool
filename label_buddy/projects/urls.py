from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include, url
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r"^$", views.index, name="index_page"),
    url(r"^projects/create$", views.project_create_view, name="create_project"),
    url(r"^projects/(?P<pk>\d+)/tasks$", views.project_page_view, name="project_page"),
    url(r"^projects/(?P<pk>\d+)/tasks/(?P<task_pk>\d+)/annotation$", views.annotate_task_view, name="annotation_page"),
    url(r"^projects/(?P<pk>\d+)/tasks/(?P<task_pk>\d+)/delete$", views.task_delete_view, name="delete_task"),
    url(r"^projects/(?P<pk>\d+)/tasks/(?P<task_pk>\d+)/list_annotations$", views.list_annotations_for_task_view, name="list_task_annotations"),
    url(r"^projects/(?P<pk>\d+)/tasks/(?P<task_pk>\d+)/list_annotations/(?P<annotation_pk>\d+)/review$", views.review_annotation_view, name="review_page"),
    url(r"^projects/(?P<pk>\d+)/tasks/(?P<task_pk>\d+)/annotation/delete$", views.annotation_delete_view, name="delete_annotation"),
    url(r"^projects/(?P<pk>\d+)/edit$", views.project_edit_view, name="edit_project"),
    url(r"^projects/(?P<pk>\d+)/delete$", views.project_delete_view, name="delete_project"),
    #API VIEWS
    path('api/v1/projects/', views.ProjectList.as_view(), name="project-list"),
    path('api/v1/projects/<int:pk>/', views.ProjectDetail.as_view(), name="specific_project"),
    path('api/v1/projects/<int:pk>/tasks', views.ProjectTasks.as_view(), name="project-list-tasks"),
    path('api/v1/root', views.api_root, name="api_root"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
