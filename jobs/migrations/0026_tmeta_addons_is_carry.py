# Generated by Django 2.2.7 on 2023-12-02 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0025_candidates_ai_matching"),
    ]

    operations = [
        migrations.AddField(
            model_name="tmeta_addons",
            name="is_carry",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
