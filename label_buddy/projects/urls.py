from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('projects/', views.ProjectList.as_view(), name="projects"),
    path('projects/<int:pk>/', views.ProjectDetail.as_view(), name="specific_project"),
]

urlpatterns = format_suffix_patterns(urlpatterns)