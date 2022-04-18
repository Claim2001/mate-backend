# Generated by Django 3.2.4 on 2021-07-23 10:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0042_alter_teachermodel_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursemodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='coursemodel',
            name='mentor',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
