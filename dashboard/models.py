import os

from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import ugettext_lazy as _

from account.base import BaseModel
from account.models import UserModel
from courses.models import get_resize_image_or_none, CourseModel

BaseCategory = (
    (0, _("Video")),
    (1, _("Books")),
)


class KnowledgeBaseModel(models.Model):
    category = models.IntegerField(choices=BaseCategory)
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='knowledge')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        old = KnowledgeBaseModel.objects.filter(pk=getattr(self, 'pk', None)).first()
        if old and self.preview and self.preview != old.preview:
            if old.preview and default_storage.exists(old.preview.path):
                os.remove(old.preview.path)
            self.preview = get_resize_image_or_none(self.preview, size=(self.preview.width, self.preview.height),
                                                    format='jpeg')
        if self.pk is None and self.preview:
            self.preview = get_resize_image_or_none(self.preview, size=(self.preview.width, self.preview.height),
                                                    format='jpeg')
        super(KnowledgeBaseModel, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'knowledge base'
        verbose_name_plural = 'knowledge base'


class KnowledgeVideoModel(models.Model):
    kn_base = models.ForeignKey(KnowledgeBaseModel, on_delete=models.CASCADE)
    title = models.TextField()
    video = models.TextField()
    description = models.TextField(null=True, blank=True)
    preview = models.ImageField(upload_to='knowledge/video', null=True, blank=True)

    def __str__(self):
        return f"{self.kn_base.title} {self.video}"

    class Meta:
        verbose_name = 'knowledge video'
        verbose_name_plural = 'knowledge videos'


class KnowledgeBookModel(models.Model):
    kn_base = models.ForeignKey(KnowledgeBaseModel, on_delete=models.CASCADE)
    title = models.TextField()
    book = models.TextField()
    description = models.TextField(null=True, blank=True)
    preview = models.ImageField(upload_to='knowledge/book', null=True, blank=True)

    def __str__(self):
        return f"{self.kn_base} {self.book}"

    class Meta:
        verbose_name = 'knowledge book'
        verbose_name_plural = 'knowledge books'


class NotificationModel(BaseModel, models.Model):
    to_user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    type = models.IntegerField()
    full_name = models.TextField(null=True, blank=True)
    lesson = models.TextField(null=True, blank=True)
    course = models.TextField(null=True, blank=True)
    seen = models.BooleanField(default=False, db_index=True)


class OrderModel(BaseModel, models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status_payment = models.IntegerField()
    click_trans_id = models.IntegerField(null=True, blank=True)


class PaymeModel(BaseModel, models.Model):
    paycom_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    paycom_time = models.CharField(max_length=100, null=True, blank=True)
    paycom_time_datetime = models.DateTimeField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    perform_time = models.DateTimeField(null=True, blank=True)
    cancel_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    amount = models.IntegerField()
    reason = models.IntegerField(null=True, blank=True)
    status_payment = models.IntegerField()


class LogsModel(BaseModel, models.Model):
    json = models.JSONField()
    url_type = models.TextField()
    merchant_trans_id = models.IntegerField()


# class BadgeModel(BaseModel, models.Model):
#     to_user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
#     text = models.TextField()
#     seen = models.BooleanField(default=False, db_index=True)
