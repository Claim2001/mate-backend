# Generated by Django 3.2.4 on 2021-07-15 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0038_lessonmodel_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursemodel',
            name='mentor',
            field=models.ManyToManyField(related_name='courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='coursemodel',
            name='teacher',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='courses', to='courses.teachermodel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursemodel',
            name='mentor',
            field=models.ManyToManyField(to='courses.TeacherModel'),
        ),
        migrations.AddField(
            model_name='teachermodel',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user'),
            preserve_default=False,
        ),
    ]
