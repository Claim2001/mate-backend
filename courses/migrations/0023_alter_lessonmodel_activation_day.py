# Generated by Django 3.2.4 on 2021-07-08 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0022_auto_20210708_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessonmodel',
            name='activation_day',
            field=models.IntegerField(),
        ),
    ]
