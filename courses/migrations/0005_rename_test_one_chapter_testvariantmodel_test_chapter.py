# Generated by Django 3.2.4 on 2021-06-28 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20210628_1042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testvariantmodel',
            old_name='test_one_chapter',
            new_name='test_chapter',
        ),
    ]
