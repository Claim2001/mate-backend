# Generated by Django 3.2.6 on 2021-09-16 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0098_userlessonmodel_recommend_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmodel',
            name='preview',
            field=models.ImageField(upload_to='project/preview'),
        ),
    ]
