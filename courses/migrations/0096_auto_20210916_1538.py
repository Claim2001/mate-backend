# Generated by Django 3.2.6 on 2021-09-16 10:38

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0095_alter_theorylabchaptermodel_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('title', models.CharField(max_length=150)),
                ('text', models.JSONField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project', to='courses.lessonmodel')),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
            },
        ),
        migrations.AddField(
            model_name='userboughtcoursemodel',
            name='complete_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userboughtcoursemodel',
            name='completed',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='userboughtcoursemodel',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userboughtcoursemodel',
            name='gpa',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userboughtcoursemodel',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='UserProjectModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('complete_time', models.IntegerField(blank=True, null=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('seen', models.BooleanField(db_index=True, default=False)),
                ('done', models.BooleanField(db_index=True, default=False)),
                ('points', models.PositiveIntegerField(blank=True, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.projectmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user project',
                'verbose_name_plural': 'user projects',
            },
        ),
        migrations.CreateModel(
            name='UserGPAHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('gpa', models.IntegerField(db_index=True)),
                ('user_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.userboughtcoursemodel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='usergpahistory',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created_at', 'updated_at'], name='courses_use_created_c654a1_brin'),
        ),
    ]