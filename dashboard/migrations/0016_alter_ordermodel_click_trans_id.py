# Generated by Django 3.2.6 on 2021-09-29 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_auto_20210929_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermodel',
            name='click_trans_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]