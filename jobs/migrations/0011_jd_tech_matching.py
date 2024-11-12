# Generated by Django 2.2.7 on 2023-10-06 11:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jobs", "0010_merge_20231006_1106"),
    ]

    operations = [
        migrations.CreateModel(
            name="jd_tech_matching",
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
                ("jd_id", models.IntegerField(null=True)),
                ("skills", models.IntegerField(default=0)),
                ("roles", models.IntegerField(default=0)),
                ("exp", models.IntegerField(default=0)),
                ("qualification", models.IntegerField(default=0)),
                ("tech_tools", models.IntegerField(default=0)),
                ("soft_skills", models.IntegerField(default=0)),
                ("industry_exp", models.IntegerField(default=0)),
                ("domain_exp", models.IntegerField(default=0)),
                ("certification", models.IntegerField(default=0)),
                ("location", models.IntegerField(default=0)),
                ("cultural_fit", models.IntegerField(default=0)),
                ("ref", models.IntegerField(default=0)),
                (
                    "user_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
