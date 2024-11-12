from django.http.response import HttpResponse
from permission.serializers import CreatePermissionSerializer, PermissionSerializer
from django.contrib.auth.models import Group, Permission
from rest_framework import generics, permissions, serializers, status
from rest_framework import response
from rest_framework.response import Response


# Permission Viewset
class PermissionAPI(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        ids = (
            1,
            3,
            4,
            5,
            6,
            7,
            9,
        )
        queryset = Permission.objects.filter(id__in=ids).order_by("order")
        serializer = PermissionSerializer(queryset, many=True)
        # this is sample data, need to add in DB
        additional = {
            "id": 1478,
            "name": "Job Workflow",
            "codename": "job_workflow",
            "order": 1478,
            "content_type": 4,
        }
        data = serializer.data
        data.append(additional)
        return Response(
            {
                "success": True,
                "data": data,
            }
        )


class CreatePermissionAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreatePermissionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        permission = serializer.save()
        return Response({"success": True, "data": permission})


class GetPermissionByRole(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PermissionSerializer

    def get(self, request, id, *args, **kwargs):
        try:
            permissions = Permission.objects.filter(group__id=id).order_by("id")
        except Permission.DoesNotExist:
            return Response(
                {"success": False, "msg": "The permission does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if "user_id" in request.GET:
            user_permissions = Permission.objects.filter(
                user__id=request.GET["user_id"]
            )
            permission_serializer = PermissionSerializer(
                user_permissions, many=True
            ).data
        else:
            permission_serializer = None
        serializer = PermissionSerializer(permissions, many=True)
        permissions = serializer.data
        additional_data = {
            "id": 1478,
            "name": "Job Workflow",
            "codename": "job_workflow",
            "order": 13,
            "content_type": 4,
        }
        permissions.append(additional_data)
        # return HttpResponse(permission_serializer)
        return Response(
            {
                "success": True,
                "data": permissions,
                "permission": permission_serializer,
            }
        )
