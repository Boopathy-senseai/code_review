# Generated by Django 2.2.7 on 2023-12-06 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0027_applicant_descriptive"),
    ]

    operations = [
        migrations.AddField(
            model_name="client_features_balance",
            name="plan_count",
            field=models.IntegerField(null=True),
        ),
    ]
