# Generated by Django 2.2.7 on 2023-08-08 10:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event_scheduler",
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
                ("event_name", models.CharField(max_length=100)),
                ("event_type", models.CharField(max_length=100)),
                ("location", models.CharField(max_length=100, null=True)),
                ("daterange", models.CharField(max_length=100)),
                ("days", models.CharField(max_length=100)),
                ("startdate", models.CharField(max_length=100)),
                ("enddate", models.CharField(max_length=100)),
                ("duration", models.CharField(max_length=100)),
                ("times_zone", models.CharField(max_length=100)),
                ("interviewer", models.CharField(max_length=100)),
                ("times_zone_display", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                ("updatedby", models.DateTimeField(auto_now_add=True, null=True)),
                ("isdeleted", models.BooleanField(default=False)),
                ("ischecked", models.CharField(default=True, max_length=100)),
                (
                    "company",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.UserHasComapny",
                    ),
                ),
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
            name="Scheduled_Time",
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
                ("index", models.IntegerField(null=True)),
                ("day", models.CharField(max_length=100, null=True)),
                ("starttime", models.CharField(max_length=100, null=True)),
                ("endtime", models.CharField(max_length=100, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "event_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule_event.Event_scheduler",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Schedule_interview",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "emp_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "event_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule_event.Event_scheduler",
                    ),
                ),
                (
                    "name",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="users.UserHasComapny",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Interview_slot",
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
                ("date", models.CharField(max_length=100)),
                ("time", models.CharField(max_length=100)),
                ("email", models.CharField(max_length=100, null=True)),
                ("startevent", models.CharField(max_length=100, null=True)),
                ("endevent", models.CharField(max_length=100, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=False)),
                ("is_checked", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_by", models.CharField(max_length=255)),
                (
                    "candidate_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobs.employer_pool",
                    ),
                ),
                (
                    "event_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule_event.Event_scheduler",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AvailbleSlot",
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
                ("date", models.CharField(max_length=100, null=True)),
                ("index", models.IntegerField(null=True)),
                ("starttime", models.CharField(max_length=100, null=True)),
                ("endtime", models.CharField(max_length=100, null=True)),
                (
                    "event_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule_event.Event_scheduler",
                    ),
                ),
            ],
        ),
    ]
