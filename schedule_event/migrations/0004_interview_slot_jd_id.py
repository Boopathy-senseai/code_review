# Generated by Django 2.2.7 on 2024-01-25 08:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0035_matching_loader"),
        ("schedule_event", "0003_auto_20230813_1759"),
    ]

    operations = [
        migrations.AddField(
            model_name="interview_slot",
            name="jd_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="jobs.JD_form",
            ),
        ),
    ]