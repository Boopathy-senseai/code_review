# Generated by Django 2.2.7 on 2023-11-28 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0016_reparsing_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="tmeta_addons",
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
                ("name", models.TextField(null=True)),
                ("currency", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="addons_plan_features",
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
                ("price", models.IntegerField(null=True)),
                ("value", models.IntegerField(null=True)),
                (
                    "addon",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobs.tmeta_addons",
                    ),
                ),
                (
                    "plan_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="jobs.tmeta_plan",
                    ),
                ),
            ],
        ),
    ]
