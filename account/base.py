from django.db import models
from django.contrib.postgres.indexes import BrinIndex
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        indexes = (
            BrinIndex(fields=('created_at', 'updated_at')),
        )
        abstract = True


class LogModel(models.Model):
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    complete_time = models.IntegerField(null=True, blank=True)

    class Meta:
        indexes = (
            BrinIndex(fields=('start_time', 'end_time', 'complete_time')),
        )
        abstract = True
