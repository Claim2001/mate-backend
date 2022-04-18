# Generated by Django 3.2.6 on 2021-09-29 11:40

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0106_coursemodel_github'),
        ('dashboard', '0014_auto_20210928_1552'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('json', models.JSONField()),
                ('url_type', models.TextField()),
                ('merchant_trans_id', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('amount', models.IntegerField()),
                ('status_payment', models.IntegerField()),
                ('click_trans_id', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='courses.coursemodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='logsmodel',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created_at', 'updated_at'], name='dashboard_l_created_e2875c_brin'),
        ),
        migrations.AddIndex(
            model_name='ordermodel',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created_at', 'updated_at'], name='dashboard_o_created_f54959_brin'),
        ),
    ]
