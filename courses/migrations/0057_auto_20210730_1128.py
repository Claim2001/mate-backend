# Generated by Django 3.2.4 on 2021-07-30 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0056_auto_20210730_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testchaptermodel',
            name='feedback_false',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='testchaptermodel',
            name='feedback_true',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='testintromodel',
            name='text',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='theorychaptermodel',
            name='text',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='theoryintromodel',
            name='text',
            field=models.JSONField(),
        ),
    ]
