# Generated by Django 2.2.7 on 2023-12-01 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0021_subscription_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jd_form",
            name="salary_curr_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="jobs.tmeta_currency_type",
            ),
        ),
    ]
