# Generated by Django 3.2.4 on 2021-07-05 12:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_auto_20210705_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlessonmodel',
            name='activation_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]