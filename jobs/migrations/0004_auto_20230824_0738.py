# Generated by Django 2.2.7 on 2023-08-24 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0003_auto_20230824_0709"),
    ]

    operations = [
        migrations.AlterField(
            model_name="score_categories",
            name="rating1",
            field=models.FloatField(default=0),
        ),
    ]
