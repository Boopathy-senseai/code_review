# Generated by Django 2.2.7 on 2023-10-26 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0012_auto_20231006_1111"),
    ]

    operations = [
        migrations.AlterField(
            model_name="matched_percentage",
            name="overall_percentage",
            field=models.FloatField(max_length=25, null=True),
        ),
    ]