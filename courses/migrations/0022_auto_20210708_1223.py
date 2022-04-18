# Generated by Django 3.2.4 on 2021-07-08 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0021_userlessonmodel_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='done',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertestintromodel',
            name='done',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheorychaptermodel',
            name='done',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheoryintromodel',
            name='done',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheorylabmodel',
            name='done',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
