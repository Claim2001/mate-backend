# Generated by Django 3.2.4 on 2021-08-19 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0084_auto_20210819_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='useransweredtestchaptermodel',
            name='answered',
            field=models.TextField(blank=True, null=True),
        ),
    ]
