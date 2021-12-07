from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import url
from . import views


# The API URLs are now determined automatically by the router
urlpatterns = [

    # API VIEWS
    path('api/v1/tasks/', views.TaskList.as_view(), name="task-list"),
    url(r"^api/v1/projects/(?P<pk>\d+)/tasks/(?P<task_pk>\d+)/annotation/save$", views.AnnotationSave.as_view(), name="save_annotation"),
    url(r"^api/v1/projects/(?P<pk>\d+)/tasks/export$", views.ExportData.as_view(), name="export_data"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
