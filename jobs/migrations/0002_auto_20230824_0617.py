# Generated by Django 2.2.7 on 2023-08-24 06:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="score_categories",
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
                ("technical", models.CharField(max_length=100, null=True)),
                ("communication_apt", models.CharField(max_length=100, null=True)),
                ("problem_solving", models.CharField(max_length=100, null=True)),
                ("collaborative_skill", models.CharField(max_length=100, null=True)),
                ("adaptability_learning", models.CharField(max_length=100, null=True)),
                ("overall_percentage", models.CharField(max_length=100, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "candidate_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobs.employer_pool",
                    ),
                ),
                (
                    "jd_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="jobs.JD_form"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="interview_scorecard",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(
            name="Mention_Candidate_notes",
        ),
    ]
