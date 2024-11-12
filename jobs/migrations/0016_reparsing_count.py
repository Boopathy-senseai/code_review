# Generated by Django 2.2.7 on 2023-11-27 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0015_merge_20231120_1133"),
    ]

    operations = [
        migrations.CreateModel(
            name="reparsing_count",
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
                ("count", models.IntegerField(default=1)),
                (
                    "jd_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="jobs.JD_form"
                    ),
                ),
            ],
        ),
    ]
