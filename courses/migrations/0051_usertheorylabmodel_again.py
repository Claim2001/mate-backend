# Generated by Django 3.2.4 on 2021-07-28 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0050_auto_20210726_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertheorylabmodel',
            name='again',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
