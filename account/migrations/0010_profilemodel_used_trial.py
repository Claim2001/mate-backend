# Generated by Django 3.2.6 on 2021-09-03 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_auto_20210812_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilemodel',
            name='used_trial',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
