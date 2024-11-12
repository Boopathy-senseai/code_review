from jobs.models import company_details
from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields import IntegerField


# Create your models here.
# class CompanyDetail(models.Model):
#     company_name = models.CharField(max_length=100)
#     company_website = models.CharField(max_length=100)
#     no_of_emp = models.IntegerField(default=0)
#     logo = models.TextField(null=True)
#     address = models.TextField(null=True)
#     city_id = models.IntegerField(null=True)
#     state_id = models.IntegerField(null=True)
#     country_id = models.IntegerField(null=True)
#     zipcode = models.CharField(max_length=100)
#     industry_type_id = models.IntegerField()
#     # recruiter_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     user = models.OneToOneField(User, on_delete=CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table = "jobs_company_details"
#         default_permissions = (),
#         # managed = False


class Department(models.Model):
    name = models.CharField(max_length=156)
    company_id = models.ForeignKey(company_details, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"
        default_permissions = ()


class UserHasComapny(models.Model):
    company = models.ForeignKey(
        company_details,
        related_name="user_has_company_company",
        on_delete=models.CASCADE,
        null=True,
        unique=False,
    )
    user = models.OneToOneField(
        User,
        related_name="user_has_company_user",
        on_delete=models.CASCADE,
        null=True,
        unique=False,
    )
    department = models.ForeignKey(
        Department,
        related_name="user_has_company_department",
        on_delete=models.CASCADE,
        null=True,
        unique=False,
    )
    invited_at = models.DateTimeField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_has_company"
        default_permissions = ()


class UserDetail(models.Model):
    user = models.OneToOneField(
        User, related_name="user_detail", on_delete=models.CASCADE, null=True
    )
    contact = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_details"
        default_permissions = ()


class UserStatus(models.Model):
    user = models.OneToOneField(
        User, related_name="status", on_delete=models.CASCADE, null=True
    )
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tmeta_user_status"
        default_permissions = ()


class UserListWithDetail(models.Model):
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    company_id = models.IntegerField()
    department_name = models.CharField(max_length=150)
    group_name = models.CharField(max_length=32)
    contact_number = models.CharField(max_length=15)
    status = models.IntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_user"
        default_permissions = ()
        managed = False


class UserWithDetail(models.Model):
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150)
    company_id = models.IntegerField()
    group_id = models.IntegerField()
    department_name = models.CharField(max_length=150)
    department_id = models.IntegerField()
    group_name = models.CharField(max_length=32)
    contact_number = models.CharField(max_length=15)
    status = models.IntegerField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_user"
        default_permissions = ()
        managed = False


class UserAction(models.Model):
    action_description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    category_id = models.IntegerField(null=True)

    class Meta:
        db_table = "user_action"
        default_permissions = ()


class UserActivity(models.Model):
    user = models.ForeignKey(
        User, related_name="user", on_delete=models.CASCADE, null=True
    )
    action = models.ForeignKey(
        UserAction, related_name="action", on_delete=models.CASCADE, null=True
    )
    action_detail = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_activity"
        default_permissions = ()


class UserActivityListModel(models.Model):
    action_description = models.TextField(null=True)
    action_detail = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category_id = models.IntegerField(null=True)

    class Meta:
        db_table = "user_action"
        default_permissions = ()
        managed = False


class CompanyHasInvite(models.Model):
    invites = models.IntegerField()
    company_id = models.ForeignKey(company_details, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_has_invites"
        default_permissions = ()
