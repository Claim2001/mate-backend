# Generated by Django 3.2.4 on 2021-07-28 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0051_usertheorylabmodel_again'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertestmodel',
            name='again',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]