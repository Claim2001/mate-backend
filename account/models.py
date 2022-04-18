import os

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import models

from django.utils.translation import ugettext_lazy as _

from account.base import BaseModel

GENDERS = (
    ('woman', _('Woman')),
    ('man', _('Man')),
)

UserModel = get_user_model()


class TokenModel(BaseModel, models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='tokens')
    code = models.CharField(max_length=5)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' | ' + self.code

    class Meta:
        verbose_name = 'token'
        verbose_name_plural = 'tokens'


Permissions = (
    (0, _("User")),
    (1, _("Student")),
    (2, _("Mentor")),
    (3, _("Admin"))
)


class ProfileModel(BaseModel, models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDERS)
    avatar = models.ImageField(upload_to='profiles', blank=True, null=True)
    permission = models.IntegerField(choices=Permissions)
    phone = models.CharField(max_length=40, null=True, blank=True, unique=True)
    used_trial = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.user.username + ' | ' + self.user.get_full_name()

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
