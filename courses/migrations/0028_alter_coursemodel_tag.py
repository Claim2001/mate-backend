# Generated by Django 3.2.4 on 2021-07-09 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0027_alter_coursemodel_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursemodel',
            name='tag',
            field=models.ManyToManyField(blank=True, null=True, to='courses.TagModel'),
        ),
    ]