# Generated by Django 2.2.7 on 2024-04-17 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0061_auto_20240416_1318"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tmeta_message_templates",
            name="status",
            field=models.BooleanField(null=True),
        ),
    ]
