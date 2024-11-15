# Generated by Django 2.2.7 on 2024-04-01 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0052_tour_data_is_steps"),
    ]

    operations = [
        migrations.CreateModel(
            name="linkedin_data",
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
                ("linkedin_id", models.IntegerField(null=True)),
                ("sourcing_data", models.TextField(null=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_by", models.CharField(max_length=500, null=True)),
            ],
        ),
    ]
