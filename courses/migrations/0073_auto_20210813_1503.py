# Generated by Django 3.2.4 on 2021-08-13 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0072_auto_20210813_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='complete_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
