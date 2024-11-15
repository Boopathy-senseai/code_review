# Generated by Django 2.2.7 on 2023-08-24 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0002_auto_20230824_0617"),
    ]

    operations = [
        migrations.RenameField(
            model_name="score_categories",
            old_name="adaptability_learning",
            new_name="rating1",
        ),
        migrations.RemoveField(
            model_name="score_categories",
            name="collaborative_skill",
        ),
        migrations.RemoveField(
            model_name="score_categories",
            name="communication_apt",
        ),
        migrations.RemoveField(
            model_name="score_categories",
            name="problem_solving",
        ),
        migrations.RemoveField(
            model_name="score_categories",
            name="technical",
        ),
        migrations.AddField(
            model_name="score_categories",
            name="rating2",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="score_categories",
            name="rating3",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="score_categories",
            name="rating4",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="score_categories",
            name="rating5",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="score_categories",
            name="overall_percentage",
            field=models.FloatField(default=0),
        ),
    ]
