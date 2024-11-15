# Generated by Django 2.2.7 on 2023-07-31 09:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Employee_workflow",
            fields=[
                ("wk_id", models.AutoField(primary_key=True, serialize=False)),
                ("pipeline_name", models.CharField(default=False, max_length=100)),
                ("is_active", models.BooleanField(default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
                ("set_as_default", models.BooleanField(default=False)),
                ("associate", models.BooleanField(default=False)),
                ("default_all", models.BooleanField(default=False)),
                (
                    "emp_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Stages_Workflow",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("stage_name", models.CharField(max_length=100, null=True)),
                ("stage_order", models.IntegerField(null=True)),
                ("stage_color", models.CharField(max_length=100, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_disabled", models.BooleanField(default=False)),
                (
                    "workflow_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobspipeline.Employee_workflow",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Stages_suggestion",
            fields=[
                ("suggestion_id", models.AutoField(primary_key=True, serialize=False)),
                ("stage_name", models.CharField(max_length=100, null=True)),
                ("stage_order", models.IntegerField(null=True)),
                ("stage_color", models.CharField(max_length=100, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_disabled", models.BooleanField(default=False)),
                (
                    "wk_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
