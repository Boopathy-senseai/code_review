# Generated by Django 2.2.7 on 2023-12-11 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0028_client_features_balance_plan_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="client_features_balance",
            name="addons_count",
            field=models.IntegerField(null=True),
        ),
    ]