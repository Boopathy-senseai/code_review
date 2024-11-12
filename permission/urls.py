from django.urls import path, include
from .api import CreatePermissionAPI, GetPermissionByRole, PermissionAPI
from knox import views as knox_view

urlpatterns = [
    path("api/permissions", PermissionAPI.as_view()),
    path("api/permissions/role_id/<int:id>", GetPermissionByRole.as_view()),
]
