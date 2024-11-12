# Generated by Django 2.2.7 on 2023-11-29 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0020_addons_plan_features_stripe_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="subscription_content",
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
                ("rich_text_content", models.TextField(null=True)),
                ("subscription_content", models.TextField(null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_difference", models.TextField(null=True)),
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
