# Generated by Django 2.2.7 on 2024-08-29 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0071_remove_matching_loader_candidate_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='job_board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(null=True)),
                ('job_board_id', models.IntegerField(null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('jd_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.JD_form')),
            ],
        ),
    ]