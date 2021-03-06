# Generated by Django 3.2.4 on 2021-07-13 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0033_auto_20210712_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonmodel',
            name='banner',
            field=models.ImageField(default=1, upload_to='lesson/banner'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lessonmodel',
            name='preview',
            field=models.ImageField(default=1, upload_to='lesson/preview'),
            preserve_default=False,
        ),
    ]
