import datetime

from django.db.models import Q

from courses.models import UserBoughtCourseModel, UserLessonModel
from courses.serializers import lesson_activate_new
from dashboard.models import NotificationModel, OrderModel


def my_cron_job():
    for a in UserBoughtCourseModel.objects.all():
        if a.expiration_date < datetime.datetime.now().date():
            NotificationModel.objects.create(to_user=a.user, type=0, course=a.course.title_lms)
            a.status = False
            a.save()


def lesson_activate():
    for a in UserLessonModel.objects.filter(activation_date__isnull=False,
                                            activation_date__lte=datetime.datetime.now().date(),
                                            available=False, lesson__active=True):
        lesson_activate_new(a)


def order_delete():
    for a in OrderModel.objects.filter(Q(status_payment=0) | Q(status_payment=1)):
        a.delete()
