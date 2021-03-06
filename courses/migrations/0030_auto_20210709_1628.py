# Generated by Django 3.2.4 on 2021-07-09 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0029_alter_coursemodel_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursemodel',
            name='image_lms',
            field=models.ImageField(default=1, upload_to='courses/lms'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coursemodel',
            name='title_lms',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
    ]
