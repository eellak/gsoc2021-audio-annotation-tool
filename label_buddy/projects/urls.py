from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('projects/', views.ProjectList.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)