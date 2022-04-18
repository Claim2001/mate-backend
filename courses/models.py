from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models
from account.base import BaseModel, LogModel
from account.models import UserModel
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.indexes import BrinIndex
import os
from io import BytesIO
from PIL import Image
from django.core.files import File


def get_resize_image_or_none(image, size, format=None):
    try:
        im = Image.open(image)
        im.thumbnail(size, Image.ANTIALIAS)
        filename = os.path.basename(image.name)
        basename = os.path.splitext(filename)[0]
        if format in ['jpeg', 'png', 'bmp'] and format != im.format:
            im = im.convert('RGB')
        else:
            format = im.format.lower()
        thumb_io = BytesIO()
        im.save(thumb_io, format)
        return File(thumb_io, name=basename + '.' + format)
    except:
        return None


class FeedbackModel(BaseModel, models.Model):
    full_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='feedbacks')
    description = models.TextField()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'feedback'
        verbose_name_plural = 'feedbacks'


class TeacherModel(BaseModel, models.Model):
    full_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='teachers')
    description = models.TextField()
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'teacher'
        verbose_name_plural = 'teachers'


class TagModel(BaseModel, models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'


class CourseModel(BaseModel, models.Model):
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name='courses')
    title = models.CharField(max_length=50)
    title_lms = models.CharField(max_length=255)
    telegram = models.TextField()
    github = models.TextField(null=True, blank=True)
    image_course_title = models.CharField(max_length=50)
    image_teacher_title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='courses')
    image_lms = models.ImageField(upload_to='courses/lms')
    teacher = models.ForeignKey(TeacherModel, on_delete=models.PROTECT, related_name='courses')
    mentor = models.ManyToManyField(TeacherModel, blank=True)
    duration = models.CharField(max_length=20)
    price = models.PositiveIntegerField()
    tag = models.ManyToManyField(TagModel, blank=True)
    active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        old = CourseModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old:
            if old and old.image and default_storage.exists(old.image.path) and self.image and self.image != old.image:
                os.remove(old.image.path)
            if old and old.image_lms and default_storage.exists(
                    old.image_lms.path) and self.image_lms and self.image_lms != old.image_lms:
                os.remove(old.image_lms.path)
            if self.image and self.image != old.image:
                self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                      format='jpeg')
            if self.image_lms and self.image_lms != old.image_lms:
                self.image_lms = get_resize_image_or_none(self.image_lms,
                                                          size=(self.image_lms.width, self.image_lms.height),
                                                          format='jpeg')
        if self.pk is None:
            if self.image:
                self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                      format='jpeg')
            if self.image_lms:
                self.image_lms = get_resize_image_or_none(self.image_lms,
                                                          size=(self.image_lms.width, self.image_lms.height),
                                                          format='jpeg')
        super(CourseModel, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'


class CourseTipsModel(BaseModel, models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name='tip')
    tip = models.CharField(max_length=255)
    sub_tip = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.tip} {self.sub_tip}"

    class Meta:
        verbose_name = 'course tip'
        verbose_name_plural = 'course tips'


class LessonModel(BaseModel, models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name='lesson')
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.CharField(verbose_name='Название', max_length=100)
    description = models.TextField()
    preview = models.ImageField(upload_to='lesson/preview')
    banner = models.ImageField(upload_to='lesson/banner')
    active = models.BooleanField(default=False, db_index=True)
    recommend_end = models.IntegerField()
    activation_day = models.IntegerField()
    lab_percentage = models.IntegerField()
    test_percentage = models.IntegerField()

    def __str__(self):
        return f"{self.course.title} {self.title}"

    def save(self, *args, **kwargs):
        old = LessonModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old:
            if old and old.preview and default_storage.exists(
                    old.preview.path) and self.preview and self.preview != old.preview:
                os.remove(old.preview.path)
            if old and old.banner and default_storage.exists(
                    old.banner.path) and self.banner and self.banner != old.banner:
                os.remove(old.banner.path)
            if self.preview and self.preview != old.preview:
                self.preview = get_resize_image_or_none(self.preview, size=(self.preview.width, self.preview.height),
                                                        format='jpeg')
            if self.banner and self.banner != old.banner:
                self.banner = get_resize_image_or_none(self.banner, size=(self.banner.width, self.banner.height),
                                                       format='jpeg')
        if self.pk is None:
            if self.preview:
                self.preview = get_resize_image_or_none(self.preview, size=(self.preview.width, self.preview.height),
                                                        format='jpeg')
            if self.banner:
                self.banner = get_resize_image_or_none(self.banner, size=(self.banner.width, self.banner.height),
                                                       format='jpeg')
        super(LessonModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'lesson'
        verbose_name_plural = 'lessons'


class TheoryModel(BaseModel, models.Model):
    lesson = models.ForeignKey(LessonModel, on_delete=models.CASCADE, related_name='theory')
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.lesson.course.title} {self.lesson.title} {self.title}"

    class Meta:
        verbose_name = 'theory'
        verbose_name_plural = 'theories'


class TheoryIntroModel(BaseModel, models.Model):
    theory = models.OneToOneField(TheoryModel, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='theory/intro')
    text = models.JSONField()

    def __str__(self):
        return f"{self.theory.lesson.course.title} {self.theory.lesson.title} {self.theory.title}"

    def save(self, *args, **kwargs):
        old = TheoryIntroModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old and self.image and self.image != old.image:
            if old.image and default_storage.exists(old.image.path):
                os.remove(old.image.path)
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        if self.pk is None and self.image:
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        super(TheoryIntroModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'theory intro'
        verbose_name_plural = 'theory intros'


class TheoryChapterModel(BaseModel, models.Model):
    theory = models.ForeignKey(TheoryModel, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    text = models.JSONField()

    def __str__(self):
        return f"{self.theory.lesson.course.title} {self.theory.lesson.title} {self.theory.title}"

    class Meta:
        verbose_name = 'theory chapter'
        verbose_name_plural = 'theory chapters'


Labs = (
    (0, _("Replit")),
    (1, _("Github")),
)


class TheoryLabChapterModel(BaseModel, models.Model):
    theory = models.ForeignKey(TheoryModel, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.CharField(max_length=500)
    embed = models.CharField(max_length=500, null=True, blank=True)
    text = models.JSONField(null=True, blank=True)
    trial = models.TextField(null=True, blank=True)
    minimum_points = models.PositiveIntegerField(blank=True, null=True)
    control = models.BooleanField(db_index=True)
    type = models.IntegerField(choices=Labs)
    project = models.BooleanField()

    def __str__(self):
        return f"{self.theory.lesson.course.title} {self.theory.lesson.title} {self.theory.title} {self.title}"

    class Meta:
        verbose_name = 'theory lab'
        verbose_name_plural = 'theory labs'


Tests = (
    (0, _("One answer")),
    (1, _("Multiple answer")),
    (2, _("Short")),
)


class TestModel(BaseModel, models.Model):
    lesson = models.ForeignKey(LessonModel, on_delete=models.CASCADE, related_name='test')
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.CharField(max_length=150)
    minimum_percentage = models.PositiveIntegerField(blank=True, null=True)
    control = models.BooleanField(db_index=True)
    timer = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.lesson.course.title} {self.lesson.title} {self.title}"

    class Meta:
        verbose_name = 'test'
        verbose_name_plural = 'tests'


class TestIntroModel(BaseModel, models.Model):
    test = models.OneToOneField(TestModel, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    title = models.TextField()
    greetings = models.TextField()
    image = models.ImageField(upload_to='test/intro')
    text = models.JSONField()

    def __str__(self):
        return f"{self.test.lesson.course.title} {self.test.lesson.title} {self.test.title}"

    def save(self, *args, **kwargs):
        old = TestIntroModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old and self.image and self.image != old.image:
            if old.image and default_storage.exists(old.image.path):
                os.remove(old.image.path)
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        if self.pk is None and self.image:
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        super(TestIntroModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'test intro'
        verbose_name_plural = 'test intros'


class TestChapterModel(BaseModel, models.Model):
    test = models.ForeignKey(TestModel, on_delete=models.CASCADE)
    author = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    type = models.IntegerField(choices=Tests)
    title = models.CharField(max_length=500)
    question = models.CharField(max_length=500)
    text = models.JSONField(null=True, blank=True)
    feedback_true = models.JSONField(null=True, blank=True)
    feedback_false = models.JSONField(null=True, blank=True)
    image = models.ImageField(upload_to='test/chapter', null=True, blank=True)
    short_answer = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.test.lesson.course.title} {self.test.lesson.title} {self.test.title} {self.title}"

    def save(self, *args, **kwargs):
        old = TestChapterModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old and self.image and self.image != old.image:
            if old.image and default_storage.exists(old.image.path):
                os.remove(old.image.path)
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        if self.pk is None and self.image:
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        super(TestChapterModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'test chapter'
        verbose_name_plural = 'test chapters'


class TestVariantModel(BaseModel, models.Model):
    test_chapter = models.ForeignKey(TestChapterModel, on_delete=models.CASCADE)
    variant = models.CharField(max_length=500)
    answer = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.test_chapter.test.lesson.course.title} {self.test_chapter.test.lesson.title} {self.test_chapter.test.title} {self.variant}"

    class Meta:
        verbose_name = 'test variant'
        verbose_name_plural = 'test variants'


class UserBoughtCourseModel(BaseModel, LogModel, models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    trial = models.BooleanField(default=False, db_index=True)
    bought_date = models.DateField()
    expiration_date = models.DateField()
    gpa = models.FloatField(default=0)
    completed = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = (
            BrinIndex(fields=('bought_date', 'expiration_date')),
        )
        verbose_name = 'user bought'
        verbose_name_plural = 'user bought'

    def __str__(self):
        return f"{self.user.username} {self.course.title}"


class UserGPAHistory(BaseModel, models.Model):
    user_course = models.ForeignKey(UserBoughtCourseModel, on_delete=models.CASCADE)
    gpa = models.FloatField(db_index=True)

    def __str__(self):
        return f"{self.user_course.user.username} {self.user_course.course.title_lms} {self.gpa}"


class UserLessonModel(BaseModel, LogModel, models.Model):
    lesson = models.ForeignKey(LessonModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)
    activation_date = models.DateField(null=True, blank=True)
    recommend_end_date = models.DateField(null=True, blank=True)
    gpa = models.FloatField(db_index=True, null=True, blank=True)

    def __str__(self):
        return f"{self.lesson.course.title} {self.lesson.title} {self.user.username}"

    class Meta:
        verbose_name = 'user lesson'
        verbose_name_plural = 'user lessons'


class UserLessonOverallModel(BaseModel, models.Model):
    user_lesson = models.OneToOneField(UserLessonModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.user_lesson.user.username} {self.user_lesson.lesson.course.title} {self.user_lesson.lesson.title}"

    class Meta:
        verbose_name = 'user lesson overall'
        verbose_name_plural = 'user lessons overall'


class UserGotLessonOverallModel(BaseModel, models.Model):
    user_overall = models.OneToOneField(UserLessonOverallModel, on_delete=models.CASCADE)
    points = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user_overall.user_lesson.user.username} {self.user_overall.user_lesson.lesson.course.title} {self.user_overall.user_lesson.lesson.title} {self.points}"

    class Meta:
        verbose_name = 'user got lesson overall'
        verbose_name_plural = 'user got lessons overall'


class UserTheoryModel(BaseModel, LogModel, models.Model):
    theory = models.ForeignKey(TheoryModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.theory.lesson.course.title} {self.theory.lesson.title} {self.theory.title} {self.user.username}"

    class Meta:
        verbose_name = 'user theory'
        verbose_name_plural = 'user theories'


class UserTheoryIntroModel(BaseModel, models.Model):
    theory_intro = models.ForeignKey(TheoryIntroModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.theory_intro.theory.lesson.course.title} {self.theory_intro.theory.lesson.title} {self.user.username}"

    class Meta:
        verbose_name = 'user theory intro'
        verbose_name_plural = 'user theory intros'


class UserTheoryChapterModel(BaseModel, LogModel, models.Model):
    theory_chapter = models.ForeignKey(TheoryChapterModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.theory_chapter.theory.lesson.course.title} {self.theory_chapter.theory.lesson.title} {self.user.username} "

    class Meta:
        verbose_name = 'user theory chapter'
        verbose_name_plural = 'user theory chapters'


class UserTheoryLabModel(BaseModel, LogModel, models.Model):
    theory_lab = models.ForeignKey(TheoryLabChapterModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False, db_index=True)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)
    again = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.theory_lab.theory.lesson.course.title} {self.theory_lab.theory.lesson.title} {self.theory_lab.title} {self.user.username}"

    class Meta:
        verbose_name = 'user theory lab'
        verbose_name_plural = 'user theory labs'


class UserAnsweredTheoryLabModel(BaseModel, LogModel, models.Model):
    user_theory_lab = models.ForeignKey(UserTheoryLabModel, on_delete=models.CASCADE)
    github = models.TextField(null=True, blank=True)
    points = models.PositiveIntegerField(null=True, blank=True)
    enough = models.BooleanField(default=False, db_index=True)
    comment = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_theory_lab.theory_lab.theory.lesson.course.title} {self.user_theory_lab.theory_lab.theory.lesson.title} {self.user_theory_lab.theory_lab.title} {self.user_theory_lab.user.username}"

    class Meta:
        verbose_name = 'user answered theory lab'
        verbose_name_plural = 'user answered theory labs'


class UserTestModel(BaseModel, LogModel, models.Model):
    test = models.ForeignKey(TestModel, on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    start = models.BooleanField(default=False, db_index=True)
    test_ending = models.DateTimeField(null=True, blank=True)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)
    again = models.BooleanField(default=False, db_index=True)
    trying = models.PositiveIntegerField(default=0, db_index=True)

    def __str__(self):
        return f"{self.test.lesson.course.title} {self.test.lesson.title} {self.test.title} {self.user.username}"

    class Meta:
        verbose_name = 'user test'
        verbose_name_plural = 'user tests'


class UserAnsweredTestModel(BaseModel, LogModel, models.Model):
    user_test_model = models.ForeignKey(UserTestModel, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(null=True, blank=True)
    enough = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_test_model.test.lesson.course.title} {self.user_test_model.test.lesson.title} {self.user_test_model.test.title} {self.user_test_model.user.username}"

    class Meta:
        verbose_name = 'user answered test'
        verbose_name_plural = 'user answered tests'


class UserTestIntroModel(BaseModel, models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    test_intro = models.ForeignKey(TestIntroModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.test_intro.test.lesson.course.title} {self.test_intro.test.lesson.title} {self.test_intro.test.title} {self.user.username}"

    class Meta:
        verbose_name = 'user test intro'
        verbose_name_plural = 'user test intros'


class UserTestChapterModel(BaseModel, LogModel, models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    test_chapter = models.ForeignKey(TestChapterModel, on_delete=models.CASCADE)
    available = models.BooleanField(default=False, db_index=True)
    seen = models.BooleanField(default=False, db_index=True)
    done = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.test_chapter.test.lesson.course.title} {self.test_chapter.test.lesson.title} {self.test_chapter.test.title} {self.test_chapter.title} {self.user.username}"

    class Meta:
        verbose_name = 'user test chapter'
        verbose_name_plural = 'user tests chapter'


class UserAnsweredTestChapterModel(BaseModel, LogModel, models.Model):
    user_test = models.ForeignKey(UserTestChapterModel, on_delete=models.CASCADE)
    answered = models.TextField(null=True, blank=True)
    correct = models.BooleanField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_test.test_chapter.test.lesson.course.title} {self.user_test.test_chapter.test.lesson.title} {self.user_test.test_chapter.test.title}{self.user_test.test_chapter.title} {self.user_test.user.username}"

    class Meta:
        verbose_name = 'user answered test chapter'
        verbose_name_plural = 'user answered tests chapter'


class RequestModel(BaseModel, models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    phone = models.CharField(max_length=40)
    course = models.ForeignKey(CourseModel, on_delete=models.PROTECT, related_name='requests')
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} | {self.course.title}'

    class Meta:
        verbose_name = 'request'
        verbose_name_plural = 'requests'


class SliderMainModel(BaseModel, models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.PROTECT, related_name='sliders', null=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='sliders')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'slider main'
        verbose_name_plural = 'slider main'


class SliderChildModel(BaseModel, models.Model):
    slider = models.ForeignKey(SliderMainModel, on_delete=models.CASCADE, related_name='children')
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f'{self.title} | {self.slider.title}'

    class Meta:
        verbose_name = 'slider child'
        verbose_name_plural = 'slider children'


class EditorImageModel(BaseModel, models.Model):
    image = models.ImageField(upload_to='archive/image')

    def __str__(self):
        return f'{self.image.name}'

    def save(self, *args, **kwargs):
        old = EditorImageModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old and self.image and self.image != old.image:
            if old.image and default_storage.exists(old.image.path):
                os.remove(old.image.path)
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        if self.pk is None and self.image:
            self.image = get_resize_image_or_none(self.image, size=(self.image.width, self.image.height),
                                                  format='jpeg')
        super(EditorImageModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'editor image'
        verbose_name_plural = 'editor images'
