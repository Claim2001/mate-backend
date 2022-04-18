# Generated by Django 3.2.4 on 2021-06-28 05:49

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0006_auto_20210628_1049'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson', to='courses.coursemodel')),
            ],
            options={
                'verbose_name': 'lesson',
                'verbose_name_plural': 'lessons',
            },
        ),
        migrations.CreateModel(
            name='TestChapterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.IntegerField(choices=[(0, 'One answer'), (1, 'Multiple answer'), (2, 'Short')])),
                ('question', models.CharField(max_length=500)),
                ('feedback_true', models.CharField(max_length=500)),
                ('feedback_false', models.CharField(max_length=500)),
                ('short_answer', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name': 'test chapter',
                'verbose_name_plural': 'test chapters',
            },
        ),
        migrations.CreateModel(
            name='TestIntroModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'test intro',
                'verbose_name_plural': 'test intros',
            },
        ),
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=150)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test', to='courses.lessonmodel')),
            ],
            options={
                'verbose_name': 'test',
                'verbose_name_plural': 'tests',
            },
        ),
        migrations.CreateModel(
            name='TheoryChapterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'theory chapter',
                'verbose_name_plural': 'theory chapters',
            },
        ),
        migrations.CreateModel(
            name='TheoryIntroModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'theory intro',
                'verbose_name_plural': 'theory intros',
            },
        ),
        migrations.CreateModel(
            name='TheoryLabChapterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=500)),
                ('embed', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'theory lab',
                'verbose_name_plural': 'theory labs',
            },
        ),
        migrations.CreateModel(
            name='TheoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=150)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='theory', to='courses.lessonmodel')),
            ],
            options={
                'verbose_name': 'theory',
                'verbose_name_plural': 'theories',
            },
        ),
        migrations.CreateModel(
            name='UserTheoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('theory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.theorymodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user theory',
                'verbose_name_plural': 'user theories',
            },
        ),
        migrations.CreateModel(
            name='UserTheoryLabModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('theory_lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.theorylabchaptermodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user theory lab',
                'verbose_name_plural': 'user theory labs',
            },
        ),
        migrations.CreateModel(
            name='UserTheoryIntroModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('theory_intro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.theoryintromodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user theory intro',
                'verbose_name_plural': 'user theory intros',
            },
        ),
        migrations.CreateModel(
            name='UserTheoryChapterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('theory_chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.theorychaptermodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user theory chapter',
                'verbose_name_plural': 'user theory chapters',
            },
        ),
        migrations.CreateModel(
            name='UserTestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.testmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user test',
                'verbose_name_plural': 'user tests',
            },
        ),
        migrations.CreateModel(
            name='UserTestIntroModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('test_intro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.testintromodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user test intro',
                'verbose_name_plural': 'user test intros',
            },
        ),
        migrations.CreateModel(
            name='UserTestChapterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('test_chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.testchaptermodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user test chapter',
                'verbose_name_plural': 'user tests chapter',
            },
        ),
        migrations.CreateModel(
            name='UserLessonOverallModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lessonmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user lesson overall',
                'verbose_name_plural': 'user lessons overall',
            },
        ),
        migrations.CreateModel(
            name='UserLessonModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('available', models.BooleanField(db_index=True, default=False)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lessonmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user lesson',
                'verbose_name_plural': 'user lessons',
            },
        ),
        migrations.CreateModel(
            name='UserGotLessonOverallModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('points', models.PositiveIntegerField()),
                ('user_overall', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.userlessonoverallmodel')),
            ],
            options={
                'verbose_name': 'user got lesson overall',
                'verbose_name_plural': 'user got lessons overall',
            },
        ),
        migrations.CreateModel(
            name='UserBoughtCourseModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=False)),
                ('bought_date', models.DateField()),
                ('expiration_date', models.DateField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.coursemodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user bought',
                'verbose_name_plural': 'user bought',
            },
        ),
        migrations.CreateModel(
            name='UserAnsweredTheoryLabModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('points', models.PositiveIntegerField(blank=True, null=True)),
                ('user_theory_lab', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.usertheorylabmodel')),
            ],
            options={
                'verbose_name': 'user answered theory lab',
                'verbose_name_plural': 'user answered theory labs',
            },
        ),
        migrations.CreateModel(
            name='UserAnsweredTestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('points', models.PositiveIntegerField(blank=True, null=True)),
                ('user_test_model', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.usertestmodel')),
            ],
            options={
                'verbose_name': 'user answered test',
                'verbose_name_plural': 'user answered tests',
            },
        ),
        migrations.CreateModel(
            name='UserAnsweredTestChapterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('answered', models.TextField(blank=True, null=True)),
                ('correct', models.BooleanField(blank=True, null=True)),
                ('user_test', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.usertestchaptermodel')),
            ],
            options={
                'verbose_name': 'user answered test chapter',
                'verbose_name_plural': 'user answered tests chapter',
            },
        ),
        migrations.AddField(
            model_name='theorylabchaptermodel',
            name='theory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.theorymodel'),
        ),
        migrations.AddField(
            model_name='theoryintromodel',
            name='theory',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.theorymodel'),
        ),
        migrations.AddField(
            model_name='theorychaptermodel',
            name='theory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.theorymodel'),
        ),
        migrations.CreateModel(
            name='TestVariantModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('variant', models.CharField(max_length=500)),
                ('answer', models.BooleanField(default=True)),
                ('test_chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.testchaptermodel')),
            ],
            options={
                'verbose_name': 'test variant',
                'verbose_name_plural': 'test variants',
            },
        ),
        migrations.AddField(
            model_name='testintromodel',
            name='test',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.testmodel'),
        ),
        migrations.AddField(
            model_name='testchaptermodel',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.testmodel'),
        ),
        migrations.AddIndex(
            model_name='userboughtcoursemodel',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['bought_date', 'expiration_date'], name='courses_use_bought__7f666e_brin'),
        ),
    ]