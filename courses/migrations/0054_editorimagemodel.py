# Generated by Django 3.2.4 on 2021-07-28 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0053_auto_20210728_1102'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditorImageModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='archive/image')),
            ],
            options={
                'verbose_name': 'editor image',
                'verbose_name_plural': 'editor images',
            },
        ),
    ]
