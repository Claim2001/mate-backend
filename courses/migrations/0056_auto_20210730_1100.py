# Generated by Django 3.2.4 on 2021-07-30 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0055_auto_20210730_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theorychaptermodel',
            name='text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='theoryintromodel',
            name='text',
            field=models.TextField(),
        ),
    ]
