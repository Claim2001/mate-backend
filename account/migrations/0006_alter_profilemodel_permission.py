# Generated by Django 3.2.4 on 2021-07-15 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20210625_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilemodel',
            name='permission',
            field=models.IntegerField(choices=[(0, 'User'), (1, 'Student'), (2, 'Mentor'), (3, 'Admin')]),
        ),
    ]