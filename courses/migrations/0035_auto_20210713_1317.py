# Generated by Django 3.2.4 on 2021-07-13 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0034_auto_20210713_1153'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursemodel',
            name='structure_1',
        ),
        migrations.RemoveField(
            model_name='coursemodel',
            name='structure_2',
        ),
        migrations.RemoveField(
            model_name='coursemodel',
            name='structure_3',
        ),
        migrations.RemoveField(
            model_name='coursemodel',
            name='structure_4',
        ),
    ]