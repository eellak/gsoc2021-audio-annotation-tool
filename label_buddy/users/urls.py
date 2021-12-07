from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

# The API URLs are now determined automatically by the router
urlpatterns = [
    url(r"^user/(?P<username>[\w@.]*)/edit$", views.edit_profile, name="edit_user"),
    # API VIEWS
    path('api/v1/users/', views.UserList.as_view(), name="user-list"),
    path('api/v1/users/<int:pk>/', views.UserDetail.as_view(), name="specific_user"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
