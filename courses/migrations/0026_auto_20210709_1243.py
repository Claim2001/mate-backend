# Generated by Django 3.2.4 on 2021-07-09 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0025_auto_20210709_1159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlessonmodel',
            name='user_course',
        ),
        migrations.RemoveField(
            model_name='usertestchaptermodel',
            name='user_lesson_test',
        ),
        migrations.RemoveField(
            model_name='usertestintromodel',
            name='user_lesson_test',
        ),
        migrations.RemoveField(
            model_name='usertestmodel',
            name='user_lesson',
        ),
        migrations.RemoveField(
            model_name='usertheorychaptermodel',
            name='user_lesson_theory',
        ),
        migrations.RemoveField(
            model_name='usertheoryintromodel',
            name='user_lesson_theory',
        ),
        migrations.RemoveField(
            model_name='usertheorylabmodel',
            name='user_lesson_theory',
        ),
        migrations.RemoveField(
            model_name='usertheorymodel',
            name='user_lesson',
        ),
        migrations.AddField(
            model_name='userlessonmodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestintromodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestmodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheorychaptermodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheoryintromodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheorylabmodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheorymodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userlessonoverallmodel',
            name='user_lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.userlessonmodel'),
        ),
    ]
