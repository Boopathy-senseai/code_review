from django.http.response import HttpResponse
from permission.serializers import PermissionSerializer
from django.contrib.auth.models import Group, Permission
from rest_framework import generics, permissions, serializers, status
from rest_framework import response
from rest_framework.response import Response
from .serializers import (
    AddPermissionGroupSerializer,
    CreateGroupSerializer,
    RoleSerializer,
)


# from models import Role,User
# Role Viewset
# Need to add 1478 in DB to complete the code
class RoleAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Group.objects.filter(id__in=[1, 2, 3])
    serializer_class = RoleSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset().order_by("id")
        serializer = RoleSerializer(queryset, many=True)
        data = serializer.data
        additional_id = 1478
        for role in data:
            role["permissions"].append(1478)
        return Response({"success": True, "data": data})


class CreateRoleAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateGroupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        group = serializer.save()
        return Response({"success": True, "data": group})


class AddRolePermissionAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddPermissionGroupSerializer

    def patch(self, request, id, *args, **kwargs):
        try:
            group = Group.objects.get(pk=id)
        except Group.DoesNotExist:
            return Response(
                {"success": False, "msg": "The role does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        ids = tuple(request.data["permissions"])

        try:
            permissions = Permission.objects.filter(id__in=ids)
        except Permission.DoesNotExist:
            return Response(
                {"success": False, "msg": "The permission does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        group.permissions.add(*permissions)
        serializer = RoleSerializer(group)
        group = serializer.data
        return Response(
            {
                "success": True,
                "data": group,
            }
        )


def manage_users(request):
    roles = Role.objects.all()
    users = User.objects.all()
    available_invites = True

    context = {"roles": roles, "users": users, "available_invites": available_invites}

    return response(context)


def invite_guest_user(request):
    if request.method == "POST":
        first_name = request.POST("first_name")
        last_name = request.POST("last_name")
        email = request.POST("email")
        contact_number = request.POST("contact_number")
        department = request.POST("department")
        role_id = request.POST("role")

        role = Role.objects.get(id=role_id)

        User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact_number=contact_number,
            department=department,
            role=role,
        )

    roles = Role.objects.all()

    context = {"roles": roles}
    return response(context)
