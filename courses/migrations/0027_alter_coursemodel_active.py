# Generated by Django 3.2.4 on 2021-07-09 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_auto_20210709_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursemodel',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
