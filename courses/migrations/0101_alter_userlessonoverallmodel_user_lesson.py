# Generated by Django 3.2.6 on 2021-09-17 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0100_auto_20210917_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlessonoverallmodel',
            name='user_lesson',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.userlessonmodel'),
        ),
    ]