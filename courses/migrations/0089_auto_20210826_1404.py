# Generated by Django 3.2.5 on 2021-08-26 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0088_usertestmodel_trying'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursemodel',
            name='telegram',
            field=models.TextField(default='a'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='theorylabchaptermodel',
            name='telegram',
            field=models.TextField(default='a'),
            preserve_default=False,
        ),
    ]
