# Generated by Django 3.1.4 on 2021-06-18 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilemodel',
            name='phone',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]