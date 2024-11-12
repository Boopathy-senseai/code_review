from django.db import models
from django.contrib.auth.models import User

# from jobs.models import JD_form


class Employee_workflow(models.Model):
    wk_id = models.AutoField(primary_key=True)
    emp_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    pipeline_name = models.CharField(max_length=100, default=False)
    is_active = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    set_as_default = models.BooleanField(default=False)
    associate = models.BooleanField(default=False)
    default_all = models.BooleanField(default=False)


class Stages_suggestion(models.Model):
    suggestion_id = models.AutoField(primary_key=True)
    wk_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stage_name = models.CharField(max_length=100, null=True)
    stage_order = models.IntegerField(null=True)
    stage_color = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_disabled = models.BooleanField(default=False)


class Stages_Workflow(models.Model):
    workflow_id = models.ForeignKey(
        Employee_workflow, on_delete=models.CASCADE, null=True
    )
    # stage_id = models.ForeignKey(Stages_suggestion,on_delete=models.CASCADE,null=True)
    stage_name = models.CharField(max_length=100, null=True)
    stage_order = models.IntegerField(null=True)
    stage_color = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_disabled = models.BooleanField(default=False)


# class pipeline_stages(models.Model):
#     pipeline_id = models.ForeignKey(Employee_workflow,on_delete=models.CASCADE,null=True)
#     stage_order = models.CharField(max_length=100,null=True)
#     stage_name = models.CharField(max_length=100,null=True)
#     stage_color = models.CharField(max_length=100,null=True )
#     created_on = models.DateField(auto_now_add=True)
#     is_active = models.BooleanField(default=False)
#     stage_length = models.IntegerField(default= 0)

# class pipeline_view(models.Model):
#     # jd_id = models.ForeignKey(JD_form,on_delete=models.CASCADE,null=True)
#     emp_id = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
#     workflow_id = models.ForeignKey(Employee_workflow,on_delete=models.CASCADE,null=True)
#     stage_id = models.CharField(max_length=100,null=True)
#     is_active = models.BooleanField(default=False)
#     created_on = models.DateTimeField(auto_now_add=True)
#     updated_by = models.CharField(max_length=500, null=True)
#     stage_order = models.CharField(max_length=100,null=True)
#     stage_name = models.CharField(max_length=100,null=True)
#     stage_color = models.CharField(max_length=100,null=True)
#     stage_length = models.IntegerField(default= 0)
