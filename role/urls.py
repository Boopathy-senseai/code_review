from django.urls import path, include
from .api import AddRolePermissionAPI, CreateRoleAPI, RoleAPI
from knox import views as knox_view

urlpatterns = [
    path("api/roles", RoleAPI.as_view()),
    path("api/roles/add/permission/<int:id>", AddRolePermissionAPI.as_view()),
]
