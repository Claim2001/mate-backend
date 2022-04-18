import base64
import os

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from account.models import UserModel, ProfileModel
from courses.models import UserLessonModel, UserLessonOverallModel, CourseModel, LessonModel, UserBoughtCourseModel, \
    UserTheoryModel, UserTestModel, UserGPAHistory, TheoryModel, TestModel, UserGotLessonOverallModel, \
    UserAnsweredTestModel, TheoryIntroModel, TheoryChapterModel, TheoryLabChapterModel, UserTheoryIntroModel, \
    UserTheoryChapterModel, UserTheoryLabModel, UserAnsweredTheoryLabModel, TestIntroModel, TestChapterModel, \
    UserTestIntroModel, UserTestChapterModel, UserAnsweredTestChapterModel, TestVariantModel
from dashboard.models import KnowledgeBaseModel, KnowledgeVideoModel, KnowledgeBookModel, NotificationModel, OrderModel, \
    PaymeModel


class OrderSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        course = validated_data['course']
        if not course.active:
            raise ParseError('Course is not active')
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['amount'] = course.price
        validated_data['status_payment'] = 0
        return super(OrderSerializer, self).create(validated_data)

    def to_representation(self, instance):
        data = {
            "merchant_trans_id": instance.id,
            "amount": instance.amount
        }
        return data

    class Meta:
        model = OrderModel
        fields = ['course', ]


class OrderPaymeSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        course = validated_data['course']
        if not course.active:
            raise ParseError('Course is not active')
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['amount'] = course.price
        validated_data['status_payment'] = 0
        return super(OrderPaymeSerializer, self).create(validated_data)

    def to_representation(self, instance):
        message = f'm=6163ffc02c68c83ea569701c;ac.order_id={instance.id};ac.course_id={instance.course.id};ac.phone={instance.user.profile.phone};a={instance.course.price * 100}'
        base64_string = base64.b64encode(message.encode('ascii')).decode("ascii")
        data = {
            "base": base64_string,
        }
        return data

    class Meta:
        model = PaymeModel
        fields = ['course', ]


class KnowledgeBaseCreateListSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        instance.category = instance.get_category_display()
        return super(KnowledgeBaseCreateListSerializer, self).to_representation(instance)

    class Meta:
        model = KnowledgeBaseModel
        fields = '__all__'


class KnowledgeBaseDetailSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        a = super(KnowledgeBaseDetailSerializer, self).to_representation(instance)
        if instance.category == 0:
            a['videos'] = KnowledgeVideoSerializer(KnowledgeVideoModel.objects.filter(kn_base=instance), many=True,
                                                   context=self.context).data
        elif instance.category == 1:
            a['books'] = KnowledgeBookSerializer(KnowledgeBookModel.objects.filter(kn_base=instance), many=True,
                                                 context=self.context).data
        return a

    class Meta:
        model = KnowledgeBaseModel
        fields = '__all__'


class KnowledgeVideoSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        if validated_data['kn_base'].category != 0:
            raise ParseError('Wrong knowledge base')
        return super(KnowledgeVideoSerializer, self).create(validated_data)

    class Meta:
        model = KnowledgeVideoModel
        fields = '__all__'


class KnowledgeBookSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        if validated_data['kn_base'].category != 1:
            raise ParseError('Wrong knowledge base')
        return super(KnowledgeBookSerializer, self).create(validated_data)

    class Meta:
        model = KnowledgeBookModel
        fields = '__all__'


class StatisticsSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar')

    def to_representation(self, instance):
        st = super(StatisticsSerializer, self).to_representation(instance)
        gpa_ou = UserBoughtCourseModel.objects.filter(user=instance)
        gpa = 0
        all_lessons = UserLessonOverallModel.objects.filter(user_lesson__user=instance,
                                                            usergotlessonoverallmodel__isnull=False).distinct()
        if 'course' in self.context['request'].query_params:
            course = self.context['request'].query_params.get('course')
            if UserBoughtCourseModel.objects.filter(user=instance, course=course).exists():
                gpa = get_object_or_404(UserBoughtCourseModel, user=instance, course=course).gpa
            all_lessons = all_lessons.filter(user_lesson__lesson__course=course).distinct()
            if 'lesson' in self.context['request'].query_params:
                gpa = 0
                lesson = self.context['request'].query_params.get('lesson')
                if UserLessonModel.objects.filter(user=instance, lesson=lesson).exists():
                    gpa = get_object_or_404(UserLessonModel, user=instance, lesson=lesson).gpa
                all_lessons = all_lessons.filter(user_lesson__lesson_id__lte=lesson)
        else:
            gpa_nt = 0
            gpa_al = 0
            for b in gpa_ou:
                gpa_al += b.gpa
                gpa_nt += 1
            try:
                gpa = round(gpa_al / gpa_nt, 1)
            except ZeroDivisionError:
                gpa = 0
        points = 0
        for a in all_lessons.filter(usergotlessonoverallmodel__isnull=False):
            points += a.usergotlessonoverallmodel.points
        st['gpa'] = gpa
        st['points'] = points
        st['full_name'] = instance.get_full_name()
        return st

    class Meta:
        model = UserModel
        fields = ['username', 'avatar']


class StatLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonModel
        fields = ['title', ]


class StatCourseSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, obj):
        return StatLessonSerializer(LessonModel.objects.filter(course=obj), many=True).data

    class Meta:
        model = CourseModel
        fields = ['title_lms', 'lessons']


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationModel
        fields = '__all__'


class HelpListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='course.title')
    telegram = serializers.CharField(source='course.telegram')

    class Meta:
        model = UserBoughtCourseModel
        fields = ['title', 'telegram']


class DashboardStudentLesson(serializers.ModelSerializer):

    def to_representation(self, instance):
        a = super(DashboardStudentLesson, self).to_representation(instance)
        a['course_title'] = instance.lesson.course.title_lms
        a['lesson_title'] = instance.lesson.title
        return a

    class Meta:
        model = UserLessonModel
        fields = ['id', 'recommend_end_date']


class ProfileDashboardSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        pm = super(ProfileDashboardSerializer, self).to_representation(instance)
        user = instance.user
        pm['full_name'] = user.get_full_name()
        pm['gpa'] = round(UserBoughtCourseModel.objects.filter(user=user).aggregate(Avg('gpa'))['gpa__avg'], 2) if \
            UserBoughtCourseModel.objects.filter(user=user).aggregate(Avg('gpa'))['gpa__avg'] is not None else None
        if pm['gpa'] is None:
            pm['gpa'] = 0.0
        all_lessons = UserLessonOverallModel.objects.filter(user_lesson__user=user, user_lesson__done=True,
                                                            usergotlessonoverallmodel__isnull=False).distinct()
        pm['points'] = 0
        for a in all_lessons:
            pm['points'] += a.usergotlessonoverallmodel.points
        users = UserModel.objects.filter(profile__permission=1, userboughtcoursemodel__trial=False)
        if UserBoughtCourseModel.objects.filter(trial=True, user=user):
            pm['position'] = None
        else:
            data = StatisticsSerializer(users, many=True, context={"request": self.context['request']}).data
            data = sorted(data, key=lambda x: (x['gpa'], x['points']), reverse=True)
            position = 0
            for b in data:
                position += 1
                if b['username'] == user.username and b['full_name'] == user.get_full_name():
                    break
            pm['position'] = position
        pm['all_users'] = UserModel.objects.filter(profile__permission=1,
                                                   userboughtcoursemodel__trial=False).count()
        pm['gpa_graph'] = []
        if UserBoughtCourseModel.objects.filter(user=user).exists():
            fd = timezone.now()
            fd_exists = False
            upg = UserGPAHistory.objects.filter(user_course__user=user).distinct().order_by('created_at')
            if upg.exists():
                fd = upg.first().created_at
                fd_exists = True
            if fd_exists:
                for i in range((timezone.now() + relativedelta(days=1) - fd).days):
                    it_date = fd + i * relativedelta(days=1)
                    gpl = 0
                    gpd = 0
                    for k in UserBoughtCourseModel.objects.filter(user=user):
                        kk = UserGPAHistory.objects.filter(user_course=k, created_at__day=it_date.date().day,
                                                           created_at__month=it_date.date().month,
                                                           created_at__year=it_date.date().year).order_by('created_at')
                        if kk.exists():
                            gpd += 1
                            gpl += kk.last().gpa
                    if gpd > 0:
                        d1 = {"date": it_date.date(),
                              "rating": round(gpl / gpd, 1)}
                        pm['gpa_graph'].append(d1)
        pm['calendar'] = []
        ulm = UserLessonModel.objects.filter(user=user, recommend_end_date__isnull=False, done=False,
                                             recommend_end_date__gt=timezone.now().date()).distinct()
        for ul in ulm:
            pm['calendar'].append(DashboardStudentLesson(ul, many=False).data)
        return pm

    class Meta:
        model = ProfileModel
        fields = ['avatar', ]


class PrepareSerializer(serializers.Serializer):
    click_trans_id = serializers.IntegerField(required=False)
    service_id = serializers.IntegerField(required=False)
    click_paydoc_id = serializers.IntegerField(required=False)
    merchant_trans_id = serializers.CharField(required=False)
    amount = serializers.IntegerField(required=False)
    action = serializers.IntegerField(required=False)
    error = serializers.IntegerField(required=False)
    error_note = serializers.CharField(required=False)
    sign_time = serializers.CharField(required=False)
    sign_string = serializers.CharField(required=False)


class PaymeSerializer(serializers.Serializer):
    click_trans_id = serializers.IntegerField(required=False)


class StatisticsCoursesSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super(StatisticsCoursesSerializer, self).to_representation(instance)
        data['author'] = instance.author.get_full_name()
        data['bought'] = UserBoughtCourseModel.objects.filter(course=instance, user__profile__permission=1,
                                                              trial=False).count()
        data['trial'] = UserBoughtCourseModel.objects.filter(course=instance, user__profile__permission=1,
                                                             trial=True).count()
        data['lesson_count'] = LessonModel.objects.filter(course=instance).count()
        data['mentor_count'] = instance.mentor.count()
        data['best_gpa'] = round(UserBoughtCourseModel.objects.filter(course=instance, usergpahistory__isnull=False,
                                                                      user__profile__permission=1).aggregate(
            Max('gpa'))['gpa__max'], 2) if \
            UserBoughtCourseModel.objects.filter(course=instance, usergpahistory__isnull=False,
                                                 user__profile__permission=1).aggregate(
                Max('gpa'))['gpa__max'] is not None else None
        data['avg_gpa'] = round(UserBoughtCourseModel.objects.filter(course=instance, usergpahistory__isnull=False,
                                                                     user__profile__permission=1).aggregate(Avg('gpa'))[
                                    'gpa__avg'], 2) if \
            UserBoughtCourseModel.objects.filter(course=instance, usergpahistory__isnull=False,
                                                 user__profile__permission=1).aggregate(Avg('gpa'))[
                'gpa__avg'] is not None else None
        data['best_points'] = round(
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson__course=instance,
                                                     user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user__profile__permission=1).aggregate(
                Max('points'))['points__max'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson__course=instance,
                                                     user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user__profile__permission=1).aggregate(
                Max('points'))['points__max'] is not None else None

        data['avg_points'] = round(
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson__course=instance,
                                                     user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user__profile__permission=1).aggregate(
                Avg('points'))['points__avg'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson__course=instance,
                                                     user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user__profile__permission=1).aggregate(
                Avg('points'))['points__avg'] is not None else None
        return data

    class Meta:
        model = CourseModel
        fields = ['id', 'title_lms', 'image_lms']


class StatisticsLessonsSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='course.title_lms')

    def to_representation(self, instance):
        data = super(StatisticsLessonsSerializer, self).to_representation(instance)
        data['author'] = instance.author.get_full_name()
        data['theory_count'] = TheoryModel.objects.filter(lesson=instance).count()
        data['test_count'] = TestModel.objects.filter(lesson=instance).count()
        data['doing'] = UserLessonModel.objects.filter(lesson=instance, available=True, done=False,
                                                       user__profile__permission=1).count()
        data['done'] = UserLessonModel.objects.filter(lesson=instance, done=True,
                                                      user__profile__permission=1).count()
        data['avg_done'] = round(UserLessonModel.objects.filter(lesson=instance, done=True, complete_time__isnull=False,
                                                                user__profile__permission=1).aggregate(
            Avg('complete_time'))['complete_time__avg'], 2) if \
            UserLessonModel.objects.filter(lesson=instance, done=True, complete_time__isnull=False,
                                           user__profile__permission=1).aggregate(
                Avg('complete_time'))['complete_time__avg'] is not None else None
        data['best_done'] = round(
            UserLessonModel.objects.filter(lesson=instance, done=True, complete_time__isnull=False,
                                           user__profile__permission=1).aggregate(Min('complete_time'))[
                'complete_time__min'], 2) if \
            UserLessonModel.objects.filter(lesson=instance, done=True, complete_time__isnull=False,
                                           user__profile__permission=1).aggregate(Min('complete_time'))[
                'complete_time__min'] is not None else None

        data['avg_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson=instance,
                                                                            user_overall__user_lesson__done=True,
                                                                            user_overall__user_lesson__user__profile__permission=1).aggregate(
            Avg('points'))['points__avg'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson=instance,
                                                     user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user__profile__permission=1).aggregate(
                Avg('points'))['points__avg'] is not None else None
        data['best_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson=instance,
                                                                             user_overall__user_lesson__done=True,
                                                                             user_overall__user_lesson__user__profile__permission=1).aggregate(
            Max('points'))['points__max'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__lesson=instance,
                                                     user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user__profile__permission=1).aggregate(
                Max('points'))['points__max'] is not None else None
        return data

    class Meta:
        model = LessonModel
        fields = ['id', 'title', 'preview', 'course']


class SThSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        a = super(SThSerializer, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTheoryModel.objects.filter(theory=instance, available=True, done=False,
                                                    user__profile__permission=1).count()
        a['done'] = UserTheoryModel.objects.filter(theory=instance, available=True, done=True,
                                                   user__profile__permission=1).count()
        a['avg_done'] = round(UserTheoryModel.objects.filter(theory=instance, done=True, complete_time__isnull=False,
                                                             user__profile__permission=1).aggregate(
            Avg('complete_time'))['complete_time__avg'], 2) if \
            UserTheoryModel.objects.filter(theory=instance, done=True, complete_time__isnull=False,
                                           user__profile__permission=1).aggregate(
                Avg('complete_time'))['complete_time__avg'] is not None else None
        a['best_done'] = round(UserTheoryModel.objects.filter(theory=instance, done=True, complete_time__isnull=False,
                                                              user__profile__permission=1).aggregate(
            Min('complete_time'))['complete_time__min'], 2) if \
            UserTheoryModel.objects.filter(theory=instance, done=True, complete_time__isnull=False,
                                           user__profile__permission=1).aggregate(
                Min('complete_time'))['complete_time__min'] is not None else None
        return a

    class Meta:
        model = TheoryModel
        fields = ['id', 'title']


class STeSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        a = super(STeSerializer, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTestModel.objects.filter(test=instance, available=True, done=False,
                                                  user__profile__permission=1).count()
        a['done'] = UserTestModel.objects.filter(test=instance, available=True, done=True,
                                                 user__profile__permission=1).count()
        a['avg_done'] = round(UserTestModel.objects.filter(test=instance, done=True, complete_time__isnull=False,
                                                           user__profile__permission=1).aggregate(
            Avg('complete_time'))['complete_time__avg'], 2) if \
            UserTestModel.objects.filter(test=instance, done=True, complete_time__isnull=False,
                                         user__profile__permission=1).aggregate(
                Avg('complete_time'))['complete_time__avg'] is not None else None
        a['best_done'] = round(UserTestModel.objects.filter(test=instance, done=True, complete_time__isnull=False,
                                                            user__profile__permission=1).aggregate(
            Min('complete_time'))['complete_time__min'], 2) if \
            UserTestModel.objects.filter(test=instance, done=True, complete_time__isnull=False,
                                         user__profile__permission=1).aggregate(
                Min('complete_time'))['complete_time__min'] is not None else None
        a['avg_try'] = round(UserTestModel.objects.filter(
            Q(test=instance) & Q(available=True) & Q(user__profile__permission=1) & (Q(done=True) | Q(
                again=True))).aggregate(
            Avg('trying'))['trying__avg'], 2) if UserTestModel.objects.filter(
            Q(test=instance) & Q(available=True) & Q(user__profile__permission=1) & (Q(done=True) | Q(
                again=True))).aggregate(Avg('trying'))['trying__avg'] is not None else None
        a['avg_points'] = round(UserAnsweredTestModel.objects.filter(user_test_model__test=instance, done=True,
                                                                     points__isnull=False,
                                                                     user_test_model__user__profile__permission=1).aggregate(
            Avg('points'))['points__avg'], 2) if \
            UserAnsweredTestModel.objects.filter(user_test_model__test=instance, done=True,
                                                 points__isnull=False,
                                                 user_test_model__user__profile__permission=1).aggregate(
                Avg('points'))['points__avg'] is not None else None
        a['best_points'] = round(UserAnsweredTestModel.objects.filter(user_test_model__test=instance, done=True,
                                                                      points__isnull=False,
                                                                      user_test_model__user__profile__permission=1).aggregate(
            Max('points'))['points__max'], 2) if \
            UserAnsweredTestModel.objects.filter(user_test_model__test=instance, done=True,
                                                 points__isnull=False,
                                                 user_test_model__user__profile__permission=1).aggregate(
                Max('points'))['points__max'] is not None else None
        return a

    class Meta:
        model = TestModel
        fields = ['id', 'title']


class StatisticsTheoryTestSerializer(serializers.ModelSerializer):
    theories_and_tests = serializers.SerializerMethodField('get_inside')

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(TheoryModel.objects.filter(lesson=obj)) + list(TestModel.objects.filter(lesson=obj)),
                      key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "TheoryModel":
                th = SThSerializer(a, many=False, context=self.context).data
                th['type'] = "Theory"
                data.append(th)
            elif a.__class__.__name__ == "TestModel":
                te = STeSerializer(a, many=False, context=self.context).data
                te['type'] = "Test"
                data.append(te)
        return data

    class Meta:
        model = LessonModel
        fields = ['title', 'banner', 'theories_and_tests']


class SThTI(serializers.ModelSerializer):

    def to_representation(self, instance):
        a = super(SThTI, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTheoryIntroModel.objects.filter(theory_intro=instance, available=True, done=False,
                                                         user__profile__permission=1).count()
        a['done'] = UserTheoryIntroModel.objects.filter(theory_intro=instance, available=True, done=True,
                                                        user__profile__permission=1).count()
        return a

    class Meta:
        model = TheoryIntroModel
        fields = ['title']


class SThTHAP(serializers.ModelSerializer):
    def to_representation(self, instance):
        a = super(SThTHAP, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTheoryChapterModel.objects.filter(theory_chapter=instance, available=True, done=False,
                                                           user__profile__permission=1).count()
        a['done'] = UserTheoryChapterModel.objects.filter(theory_chapter=instance, available=True, done=True,
                                                          user__profile__permission=1).count()
        a['avg_done'] = round(
            UserTheoryChapterModel.objects.filter(theory_chapter=instance, done=True, user__profile__permission=1,
                                                  complete_time__isnull=False).aggregate(Avg('complete_time'))[
                'complete_time__avg'], 2) if \
            UserTheoryChapterModel.objects.filter(theory_chapter=instance, done=True, user__profile__permission=1,
                                                  complete_time__isnull=False).aggregate(Avg('complete_time'))[
                'complete_time__avg'] is not None else None

        a['best_done'] = round(
            UserTheoryChapterModel.objects.filter(theory_chapter=instance, done=True, user__profile__permission=1,
                                                  complete_time__isnull=False).aggregate(Min('complete_time'))[
                'complete_time__min'], 2) if \
            UserTheoryChapterModel.objects.filter(theory_chapter=instance, done=True, user__profile__permission=1,
                                                  complete_time__isnull=False).aggregate(Min('complete_time'))[
                'complete_time__min'] is not None else None
        return a

    class Meta:
        model = TheoryChapterModel
        fields = ['title']


class SThTL(serializers.ModelSerializer):
    def to_representation(self, instance):
        a = super(SThTL, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTheoryLabModel.objects.filter(theory_lab=instance, available=True, done=False,
                                                       user__profile__permission=1).count()
        a['done'] = UserTheoryLabModel.objects.filter(theory_lab=instance, available=True, done=True,
                                                      user__profile__permission=1).count()
        a['avg_done'] = round(
            UserTheoryLabModel.objects.filter(theory_lab=instance, done=True, complete_time__isnull=False,
                                              user__profile__permission=1).aggregate(
                Avg('complete_time'))['complete_time__avg'], 2) if \
            UserTheoryLabModel.objects.filter(theory_lab=instance, done=True, complete_time__isnull=False,
                                              user__profile__permission=1).aggregate(
                Avg('complete_time'))['complete_time__avg'] is not None else None
        a['best_done'] = round(
            UserTheoryLabModel.objects.filter(theory_lab=instance, done=True, complete_time__isnull=False,
                                              user__profile__permission=1).aggregate(Min('complete_time'))[
                'complete_time__min'], 2) if \
            UserTheoryLabModel.objects.filter(theory_lab=instance, done=True, complete_time__isnull=False,
                                              user__profile__permission=1).aggregate(Min('complete_time'))[
                'complete_time__min'] is not None else None

        a['avg_points'] = round(
            UserAnsweredTheoryLabModel.objects.filter(user_theory_lab__theory_lab=instance, done=True,
                                                      user_theory_lab__done=True, enough=True,
                                                      user_theory_lab__user__profile__permission=1).aggregate(
                Avg('points'))['points__avg'], 2) if \
            UserAnsweredTheoryLabModel.objects.filter(user_theory_lab__theory_lab=instance, done=True,
                                                      user_theory_lab__done=True, enough=True,
                                                      user_theory_lab__user__profile__permission=1).aggregate(
                Avg('points'))['points__avg'] is not None else None
        a['best_points'] = round(
            UserAnsweredTheoryLabModel.objects.filter(user_theory_lab__theory_lab=instance, done=True,
                                                      user_theory_lab__done=True, enough=True,
                                                      user_theory_lab__user__profile__permission=1).aggregate(
                Max('points'))['points__max'], 2) if \
            UserAnsweredTheoryLabModel.objects.filter(user_theory_lab__theory_lab=instance, done=True,
                                                      user_theory_lab__done=True, enough=True,
                                                      user_theory_lab__user__profile__permission=1).aggregate(
                Max('points'))['points__max'] is not None else None
        tl = 0
        w = 0
        for b in UserTheoryLabModel.objects.filter(
                Q(theory_lab=instance) & Q(user__profile__permission=1) & (Q(done=True) | Q(again=True))):
            tl += 1
            w += UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=b).count()
        if tl > 0:
            tt = w / tl
        else:
            tt = 0
        a['avg_try'] = round(tt, 2)
        return a

    class Meta:
        model = TheoryLabChapterModel
        fields = ['title']


class StatisticsTheoryDetailSerializer(serializers.ModelSerializer):
    inside = serializers.SerializerMethodField()

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(TheoryIntroModel.objects.filter(theory=obj)) + list(
            TheoryChapterModel.objects.filter(theory=obj)) + list(TheoryLabChapterModel.objects.filter(theory=obj)),
                      key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "TheoryIntroModel":
                ti = SThTI(a, many=False, context=self.context).data
                data.append(ti)
            elif a.__class__.__name__ == "TheoryChapterModel":
                thap = SThTHAP(a, many=False, context=self.context).data
                data.append(thap)
            elif a.__class__.__name__ == "TheoryLabChapterModel":
                tl = SThTL(a, many=False, context=self.context).data
                data.append(tl)
        return data

    class Meta:
        model = TheoryModel
        fields = ['id', 'title', 'inside']


class STeTI(serializers.ModelSerializer):
    def to_representation(self, instance):
        a = super(STeTI, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTestIntroModel.objects.filter(test_intro=instance, available=True, done=False,
                                                       user__profile__permission=1).count()
        a['done'] = UserTestIntroModel.objects.filter(test_intro=instance, available=True, done=True,
                                                      user__profile__permission=1).count()
        return a

    class Meta:
        model = TestIntroModel
        fields = ['title']


class STeTHAP(serializers.ModelSerializer):
    def to_representation(self, instance):
        a = super(STeTHAP, self).to_representation(instance)
        a['author'] = instance.author.get_full_name()
        a['doing'] = UserTestChapterModel.objects.filter(test_chapter=instance, available=True, done=False,
                                                         user__profile__permission=1).count()
        a['done'] = UserTestChapterModel.objects.filter(test_chapter=instance, available=True, done=True,
                                                        user__profile__permission=1).count()
        a['avg_done'] = round(
            UserTestChapterModel.objects.filter(test_chapter=instance, done=True, user__profile__permission=1,
                                                complete_time__isnull=False).aggregate(Avg('complete_time'))[
                'complete_time__avg'], 2) if \
            UserTestChapterModel.objects.filter(test_chapter=instance, done=True, user__profile__permission=1,
                                                complete_time__isnull=False).aggregate(Avg('complete_time'))[
                'complete_time__avg'] is not None else None

        a['best_done'] = round(
            UserTestChapterModel.objects.filter(test_chapter=instance, done=True, user__profile__permission=1,
                                                complete_time__isnull=False).aggregate(Min('complete_time'))[
                'complete_time__min'], 2) if \
            UserTestChapterModel.objects.filter(test_chapter=instance, done=True, user__profile__permission=1,
                                                complete_time__isnull=False).aggregate(Min('complete_time'))[
                'complete_time__min'] is not None else None
        ok = 0
        ght = 0
        tt = 0
        for b in UserTestChapterModel.objects.filter(test_chapter=instance, done=True, user__profile__permission=1):
            tt += 1
            last = UserAnsweredTestChapterModel.objects.filter(user_test=b, done=True).order_by('created_at').last()
            if last:
                if last.correct:
                    ok += 1
                else:
                    ght += 1
        if tt > 0:
            gall = ok / tt
            oall = ght / tt
        else:
            gall = 0
            oall = 0
        a['avg_right'] = round(gall, 2)
        a['avg_false'] = round(oall, 2)
        return a

    class Meta:
        model = TestChapterModel
        fields = ['id', 'title']


class StatisticsTestDetailSerializer(serializers.ModelSerializer):
    inside = serializers.SerializerMethodField()

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(TestIntroModel.objects.filter(test=obj)) + list(TestChapterModel.objects.filter(test=obj)),
                      key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "TestIntroModel":
                tei = STeTI(a, many=False, context=self.context).data
                data.append(tei)
            elif a.__class__.__name__ == "TestChapterModel":
                tehap = STeTHAP(a, many=False, context=self.context).data
                data.append(tehap)
        return data

    class Meta:
        model = TestModel
        fields = ['id', 'title', 'inside']


class StatisticsUsersSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source='profile.avatar')

    def to_representation(self, instance):
        a = super(StatisticsUsersSerializer, self).to_representation(instance)
        a['full_name'] = instance.get_full_name()
        a['courses_bought'] = UserBoughtCourseModel.objects.filter(user=instance, trial=False).count()
        a['trial_courses'] = UserBoughtCourseModel.objects.filter(user=instance, trial=True).count()
        a['avg_gpa'] = round(
            UserBoughtCourseModel.objects.filter(user=instance, trial=False, usergpahistory__isnull=False).aggregate(
                Avg('gpa'))['gpa__avg'], 2) if \
            UserBoughtCourseModel.objects.filter(user=instance, trial=False, usergpahistory__isnull=False).aggregate(
                Avg('gpa'))['gpa__avg'] is not None else None
        a['best_gpa'] = round(
            UserBoughtCourseModel.objects.filter(user=instance, trial=False, usergpahistory__isnull=False).aggregate(
                Max('gpa'))['gpa__max'], 2) if \
            UserBoughtCourseModel.objects.filter(user=instance, trial=False, usergpahistory__isnull=False).aggregate(
                Max('gpa'))['gpa__max'] is not None else None
        a['all_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                         user_overall__user_lesson__user=instance).aggregate(
            Sum('points'))['points__sum'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user=instance).aggregate(
                Sum('points'))['points__sum'] is not None else None
        a['avg_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                         user_overall__user_lesson__user=instance).aggregate(
            Avg('points'))['points__avg'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user=instance).aggregate(
                Avg('points'))['points__avg'] is not None else None
        a['best_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                          user_overall__user_lesson__user=instance).aggregate(
            Max('points'))['points__max'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__user=instance).aggregate(
                Max('points'))['points__max'] is not None else None
        return a

    class Meta:
        model = UserModel
        fields = ['id', 'avatar']


class SUUBCM(serializers.ModelSerializer):
    image_lms = serializers.ImageField(source='course.image_lms')
    title = serializers.CharField(source='course.title_lms')

    def to_representation(self, instance):
        a = super(SUUBCM, self).to_representation(instance)
        a['title'] = instance.course.title_lms
        a['all_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                         user_overall__user_lesson__lesson__course=instance.course).aggregate(
            Sum('points'))['points__sum'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__lesson__course=instance.course).aggregate(
                Sum('points'))['points__sum'] is not None else None
        a['avg_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                         user_overall__user_lesson__lesson__course=instance.course).aggregate(
            Avg('points'))['points__avg'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__lesson__course=instance.course).aggregate(
                Avg('points'))['points__avg'] is not None else None
        a['best_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                          user_overall__user_lesson__lesson__course=instance.course).aggregate(
            Max('points'))['points__max'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__lesson__course=instance.course).aggregate(
                Max('points'))['points__max'] is not None else None
        all1 = UserLessonModel.objects.filter(lesson__course__userboughtcoursemodel=instance, user=instance.user,
                                              lesson__active=True).count()
        down = UserLessonModel.objects.filter(lesson__course__userboughtcoursemodel=instance, user=instance.user,
                                              lesson__active=True, done=True).count()
        a["all_lessons"] = all1
        a["done_lessons"] = down
        try:
            a["percentage"] = round(down * 100 / all1, 2)
        except ZeroDivisionError:
            a["percentage"] = 0
        return a

    class Meta:
        model = UserBoughtCourseModel
        fields = ['id', 'title', 'image_lms', 'expiration_date', 'gpa', 'completed', 'status']


class StatUserDetailSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='profile.avatar')

    def get_courses(self, obj):
        return SUUBCM(
            UserBoughtCourseModel.objects.filter(user=obj, trial=False, course__active=True).order_by(
                'course__title_lms'), many=True, context=self.context).data

    def to_representation(self, instance):
        a = super(StatUserDetailSerializer, self).to_representation(instance)
        a['full_name'] = instance.get_full_name()
        return a

    class Meta:
        model = UserModel
        fields = ['id', 'avatar', 'courses']


class SUULM(serializers.ModelSerializer):
    title = serializers.CharField(source='lesson.title')
    preview = serializers.ImageField(source='lesson.preview')

    def to_representation(self, instance):
        a = super(SUULM, self).to_representation(instance)
        if UserGotLessonOverallModel.objects.filter(user_overall__user_lesson=instance):
            a['points'] = get_object_or_404(UserGotLessonOverallModel, user_overall__user_lesson=instance).points
        else:
            a['points'] = None
        return a

    class Meta:
        model = UserLessonModel
        fields = ['id', 'title', 'preview', 'available', 'done', 'activation_date', 'start_time', 'end_time',
                  'complete_time']


class StatisticsUserCourseSerializer(serializers.ModelSerializer):
    image_lms = serializers.ImageField(source='course.image_lms')
    title = serializers.CharField(source='course.title_lms')
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, obj):
        return SUULM(
            UserLessonModel.objects.filter(lesson__active=True, user=obj.user, lesson__course=obj.course).order_by(
                'created_at'), many=True, context=self.context).data

    def to_representation(self, instance):
        a = super(StatisticsUserCourseSerializer, self).to_representation(instance)
        a['title'] = instance.course.title_lms
        a['all_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                         user_overall__user_lesson__lesson__course=instance.course).aggregate(
            Sum('points'))['points__sum'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__lesson__course=instance.course).aggregate(
                Sum('points'))['points__sum'] is not None else None
        a['avg_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                         user_overall__user_lesson__lesson__course=instance.course).aggregate(
            Avg('points'))['points__avg'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__lesson__course=instance.course).aggregate(
                Avg('points'))['points__avg'] is not None else None
        a['best_points'] = round(UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                                          user_overall__user_lesson__lesson__course=instance.course).aggregate(
            Max('points'))['points__max'], 2) if \
            UserGotLessonOverallModel.objects.filter(user_overall__user_lesson__done=True,
                                                     user_overall__user_lesson__lesson__course=instance.course).aggregate(
                Max('points'))['points__max'] is not None else None
        all1 = UserLessonModel.objects.filter(lesson__course__userboughtcoursemodel=instance, user=instance.user,
                                              lesson__active=True).count()
        down = UserLessonModel.objects.filter(lesson__course__userboughtcoursemodel=instance, user=instance.user,
                                              lesson__active=True, done=True).count()
        a["all_lessons"] = all1
        a["done_lessons"] = down
        try:
            a["percentage"] = round(down * 100 / all1, 2)
        except ZeroDivisionError:
            a["percentage"] = 0
        return a

    class Meta:
        model = UserBoughtCourseModel
        fields = ['id', 'title', 'image_lms', 'expiration_date', 'gpa', 'completed', 'status', 'lessons']


class SUTH(serializers.ModelSerializer):
    title = serializers.CharField(source='theory.title')

    class Meta:
        model = UserTheoryModel
        fields = ['id', 'title', 'available', 'done', 'start_time', 'end_time', 'complete_time']


class SUTE(serializers.ModelSerializer):
    title = serializers.CharField(source='test.title')

    def to_representation(self, instance):
        a = super(SUTE, self).to_representation(instance)
        if instance.done:
            a['points'] = UserAnsweredTestModel.objects.filter(user_test_model=instance, user_test_model__done=True,
                                                               done=True).order_by('created_at').last().points
        else:
            a['points'] = None
        return a

    class Meta:
        model = UserTestModel
        fields = ['id', 'title', 'available', 'done', 'start_time', 'end_time', 'complete_time', 'trying']


class StatisticsUserLessonSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='lesson.title')
    banner = serializers.ImageField(source='lesson.banner')
    inside = serializers.SerializerMethodField()

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(UserTheoryModel.objects.filter(user=obj.user, theory__lesson=obj.lesson)) + list(
            UserTestModel.objects.filter(user=obj.user, test__lesson=obj.lesson)), key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "UserTheoryModel":
                utm = SUTH(a, many=False, context=self.context).data
                utm['type'] = "Theory"
                data.append(utm)
            elif a.__class__.__name__ == "UserTestModel":
                utm = SUTE(a, many=False, context=self.context).data
                utm['type'] = "Test"
                data.append(utm)
        return data

    class Meta:
        model = UserLessonModel
        fields = ['id', 'title', 'banner', 'inside']


class SUTHTI(serializers.ModelSerializer):
    title = serializers.CharField(source='theory_intro.title')

    class Meta:
        model = UserTheoryIntroModel
        fields = ['id', 'title', 'available', 'done']


class SUTHTHAP(serializers.ModelSerializer):
    title = serializers.CharField(source='theory_chapter.title')

    class Meta:
        model = UserTheoryChapterModel
        fields = ['id', 'title', 'start_time', 'end_time', 'complete_time', 'available', 'done']


class SUTHTLAB(serializers.ModelSerializer):
    title = serializers.CharField(source='theory_lab.title')

    def to_representation(self, instance):
        a = super(SUTHTLAB, self).to_representation(instance)
        a['try'] = UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=instance).count()
        if instance.done:
            a['points'] = UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=instance, done=True).order_by(
                'created_at').last().points
        else:
            a['points'] = None
        return a

    class Meta:
        model = UserTheoryLabModel
        fields = ['id', 'title', 'start_time', 'end_time', 'complete_time', 'available', 'done', 'again']


class StatisticsUserTheorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='theory.title')
    inside = serializers.SerializerMethodField()

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(UserTheoryIntroModel.objects.filter(user=obj.user, theory_intro__theory=obj.theory)) + list(
            UserTheoryChapterModel.objects.filter(user=obj.user, theory_chapter__theory=obj.theory)) + list(
            UserTheoryLabModel.objects.filter(user=obj.user, theory_lab__theory=obj.theory)),
                      key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "UserTheoryIntroModel":
                u = SUTHTI(a, many=False, context=self.context).data
                data.append(u)
            elif a.__class__.__name__ == "UserTheoryChapterModel":
                u = SUTHTHAP(a, many=False, context=self.context).data
                data.append(u)
            elif a.__class__.__name__ == "UserTheoryLabModel":
                u = SUTHTLAB(a, many=False, context=self.context).data
                data.append(u)
        return data

    class Meta:
        model = UserTheoryModel
        fields = ['id', 'title', 'inside']


class SUTETI(serializers.ModelSerializer):
    title = serializers.CharField(source='test_intro.title')

    class Meta:
        model = UserTestIntroModel
        fields = ['id', 'title', 'available', 'done']


class SUTETHAP(serializers.ModelSerializer):
    title = serializers.CharField(source='test_chapter.title')

    class Meta:
        model = UserTestChapterModel
        fields = ['id', 'title', 'available', 'done', 'start_time', 'end_time', 'complete_time']


class StatisticsUserTestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='test.title')
    inside = serializers.SerializerMethodField()

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(UserTestIntroModel.objects.filter(user=obj.user, test_intro__test=obj.test)) + list(
            UserTestChapterModel.objects.filter(user=obj.user, test_chapter__test=obj.test)),
                      key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "UserTestIntroModel":
                ut = SUTETI(a, many=False, context=self.context).data
                data.append(ut)
            elif a.__class__.__name__ == "UserTestChapterModel":
                ut = SUTETHAP(a, many=False, context=self.context).data
                data.append(ut)
        return data

    class Meta:
        model = UserTestModel
        fields = ['id', 'title', 'inside']
