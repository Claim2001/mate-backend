from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from courses.models import UserBoughtCourseModel, LessonModel, UserLessonModel, TheoryModel, TestModel, UserTheoryModel, \
    TheoryIntroModel, UserTheoryIntroModel, TheoryChapterModel, TheoryLabChapterModel, UserTheoryChapterModel, \
    UserTheoryLabModel, UserTestModel, UserTestIntroModel, TestIntroModel, TestChapterModel, UserTestChapterModel, \
    UserLessonOverallModel


def index_in_list(a_list, index):
    return index < len(a_list)


def admin_attach(course, user):
    ubm = UserBoughtCourseModel.objects.create(course=course, user=user, status=True,
                                               bought_date=datetime.now().date(), start_time=timezone.now(),
                                               expiration_date=datetime.now().date() + relativedelta(years=1000))
    rep_att(ubm, course, user)


def rep_att(ubm, course, user):
    lm = LessonModel.objects.filter(course=course).order_by('created_at')
    for a in lm:
        ov_all = False
        phek = True
        if LessonModel.objects.filter(course=course).exists():
            for ll in LessonModel.objects.filter(course=course, pk__lt=a.pk):
                if ll.active:
                    phek = False
        if a.activation_day == 0 and (lm.first() == a or phek):
            UserLessonModel.objects.create(available=True, lesson=a, user=user, activation_date=ubm.bought_date,
                                           recommend_end_date=ubm.bought_date + relativedelta(days=a.recommend_end))
        else:
            UserLessonModel.objects.create(lesson=a, user=user)
        all1 = sorted(list(TheoryModel.objects.filter(lesson=a)) + list(TestModel.objects.filter(lesson=a)),
                      key=lambda x: x.created_at)
        if UserLessonModel.objects.get(lesson=a, user=user).available:
            avail = True
        else:
            avail = False
        for b in all1:
            if b.__class__.__name__ == "TheoryModel":
                UserTheoryModel.objects.create(available=avail, theory=b, user=user)
                for intro in TheoryIntroModel.objects.filter(theory=b):
                    UserTheoryIntroModel.objects.create(available=avail, user=user, theory_intro=intro)
                all2 = sorted(list(TheoryChapterModel.objects.filter(theory=b)) + list(
                    TheoryLabChapterModel.objects.filter(theory=b)), key=lambda x: x.created_at)
                for t in all2:
                    if t.__class__.__name__ == "TheoryChapterModel":
                        UserTheoryChapterModel.objects.create(user=user, theory_chapter=t)
                    elif t.__class__.__name__ == "TheoryLabChapterModel":
                        UserTheoryLabModel.objects.create(theory_lab=t, user=user)
                        ov_all = True
                avail = False
            elif b.__class__.__name__ == "TestModel":
                UserTestModel.objects.create(available=avail, test=b, user=user)
                for te_int in TestIntroModel.objects.filter(test=b):
                    UserTestIntroModel.objects.create(test_intro=te_int, user=user, available=avail)
                for te_hap in TestChapterModel.objects.filter(test=b).order_by('created_at'):
                    UserTestChapterModel.objects.create(test_chapter=te_hap, user=user)
                    ov_all = True
                avail = False
        ul = UserLessonModel.objects.get(user=user, lesson=a)
        if ov_all:
            UserLessonOverallModel.objects.create(user_lesson=ul)
