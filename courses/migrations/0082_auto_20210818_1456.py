# Generated by Django 3.2.4 on 2021-08-18 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0081_rename_end_date_usertestmodel_test_ending'),
    ]

    operations = [
        migrations.AddField(
            model_name='useransweredtestchaptermodel',
            name='complete_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtestchaptermodel',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtestchaptermodel',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtestmodel',
            name='complete_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtestmodel',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtestmodel',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtheorylabmodel',
            name='complete_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtheorylabmodel',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useransweredtheorylabmodel',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]