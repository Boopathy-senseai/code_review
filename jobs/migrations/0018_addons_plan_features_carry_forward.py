# Generated by Django 2.2.7 on 2023-11-28 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0017_addons_plan_features_tmeta_addons"),
    ]

    operations = [
        migrations.AddField(
            model_name="addons_plan_features",
            name="carry_forward",
            field=models.BooleanField(default=False),
        ),
    ]
