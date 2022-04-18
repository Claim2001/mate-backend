# Generated by Django 3.2.4 on 2021-07-05 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_alter_teachermodel_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlessonoverallmodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertestchaptermodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertestintromodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertestmodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheorychaptermodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheoryintromodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheorylabmodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='usertheorymodel',
            name='seen',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
