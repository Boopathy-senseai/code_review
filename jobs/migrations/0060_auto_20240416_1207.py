# Generated by Django 2.2.7 on 2024-04-16 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0059_auto_20240411_0745"),
    ]

    operations = [
        migrations.AddField(
            model_name="tmeta_message_templates",
            name="stage",
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name="tmeta_message_templates",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]
