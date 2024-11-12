from django.db import models
from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.models import Permission


# Permission Serializer
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class CreatePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission

        def create(self, data):
            group = Permission.objects.create_group(data)
            return group


# class AddPermissionGroup(serializers.ModelSerializer):
#     class Meta:
#         model = Group

#         def create(self, data):
#             group = Group.objects.create_group(data)
#             return group;
