# Generated by Django 3.2.5 on 2021-08-26 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0089_auto_20210826_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theorylabchaptermodel',
            name='embed',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='theorylabchaptermodel',
            name='telegram',
            field=models.TextField(blank=True, null=True),
        ),
    ]
