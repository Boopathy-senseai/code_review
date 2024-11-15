# Generated by Django 2.2.7 on 2024-03-18 09:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0041_auto_20240316_1658"),
    ]

    operations = [
        migrations.CreateModel(
            name="template_stage",
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
                (
                    "stages",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobs.pipeline_view",
                    ),
                ),
                (
                    "templates",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobs.tmeta_automation_template",
                    ),
                ),
            ],
        ),
    ]
