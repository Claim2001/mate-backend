# Generated by Django 3.2.4 on 2021-07-06 07:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_alter_knowledgevideomodel_kn_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledgevideomodel',
            name='kn_base',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.knowledgebasemodel'),
        ),
    ]
