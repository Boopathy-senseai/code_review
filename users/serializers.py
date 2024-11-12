from django.core.exceptions import ValidationError
from jobs.models import company_details
from users.models import (
    CompanyHasInvite,
    Department,
    UserAction,
    UserActivity,
    UserActivityListModel,
    UserDetail,
    UserHasComapny,
    UserListWithDetail,
    UserStatus,
    UserWithDetail,
)
from django.db import models
from django.db.models import fields
from rest_framework import serializers, status, viewsets
from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password
from rest_framework.validators import UniqueValidator


# User Serializer
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        fields = (
            "id",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = company_details
        fields = (
            "id",
            "company_name",
            "company_website",
            "no_of_emp",
            "logo",
            "address",
            "city_id",
            "state_id",
            "country_id",
            "zipcode",
            "industry_type_id",
        )


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name", "company_id")


class UserHasCompanySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = UserHasComapny
        fields = ("id", "company_id", "user_id", "department_id", "user", "department")


class UserStatusSerializer(serializers.ModelSerializer):
    # user = UserSerializer(source='user_id', required=False)
    class Meta:
        model = UserStatus
        fields = ("id", "status", "user_id")


class GetUserHasCompanySerializer(serializers.ModelSerializer):
    user = UserSerializer(source="user_id", required=False)
    department = DepartmentSerializer(source="department_id", required=False)
    status = UserStatusSerializer(source="user", required=False)
    company = CompanySerializer(source="company_id", required=False)

    class Meta:
        model = UserHasComapny
        fields = (
            "id",
            "company_id",
            "user_id",
            "department_id",
            "user",
            "department",
            "status",
            "company",
        )

        # depth = 1


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ("id", "contact", "user_id")


class UserListWithDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserListWithDetail
        fields = "__all__"


class UserWithDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWithDetail
        fields = "__all__"


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
        )
        # related_fields = ['status', 'user_has_company_user', 'user_detail', 'groups']
        # depth = 1

    # status = serializers.BooleanField(source='status.status')
    # contact = serializers.CharField(source='user_detail.contact')
    # department = UserHasCompanySerializer(source='user_has_company_user',read_only=True)
    # groups = GroupSerializer(many=True, read_only=True)
    # department = serializers.BooleanField(source='status.status')


from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials Passed.")


# User Invite Serializer
class UserInviteSerializer(serializers.ModelSerializer):
    detail = UserDetailSerializer(required=False)
    status = UserStatusSerializer(required=True)
    department = DepartmentSerializer(required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "detail",
            "status",
            "department",
        )

    def create(self, validated_data):
        detail = validated_data.pop("detail")
        status = validated_data.pop("status")
        department = validated_data.pop("department")
        company = company_details.objects.get(id=self.context["company_id"])

        try:
            new_department = Department.objects.get(name=department["name"])
        except Department.DoesNotExist:
            new_department = Department.objects.create(
                name=department["name"], company_id=company
            )

        user = User.objects.create(**validated_data)
        detail["user"] = user
        status["user"] = user
        department["user"] = user
        department["company"] = company
        department["department"] = new_department
        del department["name"]
        UserDetail.objects.create(**detail)
        UserStatus.objects.create(**status)
        UserHasComapny.objects.create(**department)
        return user

    def update(self, instance, validated_data):
        detail = validated_data.pop("detail")
        status = validated_data.pop("status")
        department = validated_data.pop("department")
        company = company_details.objects.get(id=self.context["company_id"])

        try:
            new_department = Department.objects.get(name=department["name"])
        except Department.DoesNotExist:
            new_department = Department.objects.create(
                name=department["name"], company_id=company
            )

        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("email", instance.email)
        instance.save()
        user_id = self.context["pk"]
        user_details = UserDetail.objects.get(user=instance)
        user_details.contact = detail.get("contact")
        user_details.save()
        # user_status = UserStatus.objects.get(user = instance)
        # user_status.status = status.get('status')
        # user_status.save()
        user_company = UserHasComapny.objects.get(user=instance)
        user_company.department = new_department
        user_company.save()
        return instance


# User Update Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    detail = UserDetailSerializer(required=True)
    status = UserStatusSerializer(required=True)
    department = DepartmentSerializer(required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "detail",
            "status",
            "department",
        )


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityListModel
        fields = "__all__"


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = "__all__"


class CompanyInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyHasInvite
        fields = "__all__"
