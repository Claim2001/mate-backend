# Generated by Django 3.2.6 on 2021-09-03 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0093_theorylabchaptermodel_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='userboughtcoursemodel',
            name='trial',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]