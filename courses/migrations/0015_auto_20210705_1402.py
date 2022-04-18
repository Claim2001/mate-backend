# Generated by Django 3.2.4 on 2021-07-05 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_auto_20210705_1246'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tagmodel',
            options={'verbose_name': 'tag', 'verbose_name_plural': 'tags'},
        ),
        migrations.RemoveIndex(
            model_name='tagmodel',
            name='courses_tag_created_5f28d2_brin',
        ),
        migrations.AddField(
            model_name='lessonmodel',
            name='activated',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
