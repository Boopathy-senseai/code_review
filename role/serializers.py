from django.db import models
from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.models import Group


# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

        def create(self, data):
            group = Group.objects.create_group(data)
            return group


class AddPermissionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

        def create(self, data):
            group = Group.objects.create_group(data)
            return group
