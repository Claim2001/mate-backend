# Generated by Django 3.2.4 on 2021-07-24 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0044_alter_coursemodel_mentor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursemodel',
            name='mentor',
            field=models.ManyToManyField(blank=True, to='courses.TeacherModel'),
        ),
    ]
