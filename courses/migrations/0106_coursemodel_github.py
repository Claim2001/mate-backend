# Generated by Django 3.2.6 on 2021-09-23 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0105_auto_20210920_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursemodel',
            name='github',
            field=models.TextField(blank=True, null=True),
        ),
    ]