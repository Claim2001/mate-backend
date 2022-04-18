# Generated by Django 3.2.4 on 2021-07-09 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0024_auto_20210709_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlessonmodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertestchaptermodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertestintromodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertestmodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertheorychaptermodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertheoryintromodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertheorylabmodel',
            name='user',
        ),
        migrations.RemoveField(
            model_name='usertheorymodel',
            name='user',
        ),
        migrations.AddField(
            model_name='userlessonmodel',
            name='user_course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.userboughtcoursemodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='user_lesson_test',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.usertestmodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestintromodel',
            name='user_lesson_test',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.usertestmodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertestmodel',
            name='user_lesson',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.userlessonmodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheorychaptermodel',
            name='user_lesson_theory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.usertheorymodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheoryintromodel',
            name='user_lesson_theory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.usertheorymodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheorylabmodel',
            name='user_lesson_theory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.usertheorymodel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usertheorymodel',
            name='user_lesson',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='courses.userlessonmodel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userlessonoverallmodel',
            name='user_lesson',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.userlessonmodel'),
        ),
    ]