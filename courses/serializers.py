from dateutil.relativedelta import *
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.generics import get_object_or_404
from account.models import UserModel, ProfileModel
from courses.models import CourseModel, RequestModel, FeedbackModel, SliderMainModel, SliderChildModel, \
    UserBoughtCourseModel, LessonModel, UserLessonModel, TheoryModel, TestModel, UserTheoryModel, UserTestModel, \
    UserTheoryIntroModel, TheoryIntroModel, TheoryChapterModel, UserTheoryChapterModel, TheoryLabChapterModel, \
    UserTheoryLabModel, TestIntroModel, UserTestIntroModel, TestChapterModel, CourseTipsModel, \
    UserTestChapterModel, TestVariantModel, TagModel, UserLessonOverallModel, TeacherModel, EditorImageModel, \
    UserAnsweredTheoryLabModel, UserAnsweredTestModel, UserGotLessonOverallModel, UserAnsweredTestChapterModel, \
    UserGPAHistory
from courses.utils import index_in_list, admin_attach, rep_att
from dashboard.models import NotificationModel


def end_test(request, user_test):
    user_test = get_object_or_404(UserTestModel, id=user_test, done=False, seen=True, available=True)
    if request.user == user_test.user:
        user = request.user
    else:
        raise ParseError("Wrong user")
    if not user_test.seen:
        raise ParseError("Student must see it")
    if not user_test.available:
        raise ParseError("Test is not available")
    if not user_test.start:
        raise ParseError("Test is not started")
    test = user_test.test
    tries = user_test.trying
    correct_count = 0
    user_chapters = UserTestChapterModel.objects.filter(user=user, test_chapter__test=test).distinct()
    for a in user_chapters:
        if UserAnsweredTestChapterModel.objects.filter(user_test=a).distinct().count() < tries:
            while UserAnsweredTestChapterModel.objects.filter(user_test=a).distinct().count() < tries:
                UserAnsweredTestChapterModel.objects.create(user_test=a, correct=False, done=True)
        UserAnsweredTestChapterModel.objects.filter(user_test=a, correct=None).update(correct=False, done=True)
    for b in user_chapters:
        last_answer = UserAnsweredTestChapterModel.objects.filter(user_test=b).order_by('created_at').distinct().last()
        if last_answer.correct:
            correct_count += 1
    get_percentage = (correct_count * 100) / user_chapters.count()
    if test.control:
        enough = True
    elif test.minimum_percentage and get_percentage >= test.minimum_percentage:
        enough = True
    else:
        enough = False
    test_answer = UserAnsweredTestModel.objects.filter(user_test_model=user_test, done=False).order_by(
        'created_at').last()
    test_answer.done = True
    test_answer.points = get_percentage
    test_answer.enough = enough
    test_answer.end_time = timezone.now()
    test_answer.complete_time = (test_answer.end_time - test_answer.start_time).total_seconds()
    test_answer.save()
    if test.control or enough or (not test.control and enough):
        user_chapters.update(seen=True, done=True)
        user_test.start = False
        user_test.again = False
        if not user_test.done and not user_test.end_time:
            user_test.end_time = timezone.now()
            user_test.complete_time = (user_test.end_time - user_test.start_time).total_seconds()
        user_test.done = True
        user_test.save()
        lesson = test.lesson
        all1 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=lesson, user=user)) + list(
            UserTestModel.objects.filter(test__lesson=lesson, user=user)), key=lambda x: x.created_at)
        ind = all1.index(user_test) + 1
        if index_in_list(all1, ind):
            unlock_next(all1, ind, user_test)
        else:
            count_points(lesson=lesson, user=user)
    elif not test.control and not enough:
        user_chapters.update(done=False, seen=False, end_time=None, available=False, complete_time=None)
        UserTestIntroModel.objects.filter(user=user, test_intro__test=test).update(seen=False, done=False)
        user_test.start = False
        user_test.seen = False
        user_test.again = True
        user_test.save()


def unlock_next(all1, ind, instance):
    all1[ind].available = True
    all1[ind].save()
    if all1[ind].__class__.__name__ == "UserTheoryModel":
        if TheoryIntroModel.objects.filter(theory=all1[ind].theory).exists():
            UserTheoryIntroModel.objects.filter(theory_intro=TheoryIntroModel.objects.get(theory=all1[ind].theory),
                                                user=instance.user).update(available=True)
    elif all1[ind].__class__.__name__ == "UserTestModel":
        if TestIntroModel.objects.filter(test=all1[ind].test).exists():
            UserTestIntroModel.objects.filter(test_intro=TestIntroModel.objects.get(test=all1[ind].test),
                                              user=instance.user).update(available=True)


def lesson_activate_new(a):
    if UserBoughtCourseModel.objects.get(user=a.user, course=a.lesson.course).trial:
        NotificationModel.objects.create(to_user=a.user, type=1)
    if a and a.activation_date and a.activation_date <= timezone.now().date() and not UserBoughtCourseModel.objects.get(
            user=a.user, course=a.lesson.course).trial and a.lesson.active:
        l1 = get_object_or_404(LessonModel, userlessonmodel=a)
        lesson_pv = LessonModel.objects.filter(course=l1.course, pk__lt=l1.pk, active=True).order_by('-pk').first()
        l2 = UserLessonModel.objects.filter(lesson=lesson_pv, user=a.user).first()
        if LessonModel.objects.filter(course=l1.course).first() == l1 or l2.done:
            NotificationModel.objects.create(to_user=a.user, type=2, lesson=a.lesson.title,
                                             course=a.lesson.course.title_lms)
            a.available = True
            a.save()
            all1 = sorted(list(TheoryModel.objects.filter(lesson=a.lesson)) + list(
                TestModel.objects.filter(lesson=a.lesson)), key=lambda x: x.created_at)
            if all1[0].__class__.__name__ == "TheoryModel":
                UserTheoryModel.objects.filter(user=a.user, theory=all1[0]).update(available=True)
                UserTheoryIntroModel.objects.filter(user=a.user, theory_intro__theory=all1[0]).update(
                    available=True)
            elif all1[0].__class__.__name__ == "TestModel":
                UserTestModel.objects.filter(user=a.user, test=all1[0]).update(available=True)
                UserTestIntroModel.objects.filter(user=a.user, test_intro__test=all1[0]).update(available=True)


def count_points(lesson, user):
    ove = True
    u = get_object_or_404(UserLessonModel, lesson=lesson, user=user)
    if UserTheoryLabModel.objects.filter(user=user, theory_lab__theory__lesson=lesson).exists():
        for a in UserTheoryLabModel.objects.filter(user=user, theory_lab__theory__lesson=lesson):
            if not UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=a, enough=True).exists() or a.again:
                ove = False
    if UserTestModel.objects.filter(user=user, test__lesson=lesson).exists():
        for b in UserTestModel.objects.filter(user=user, test__lesson=lesson):
            if not UserAnsweredTestModel.objects.filter(user_test_model=b, enough=True).exists() or b.again:
                ove = False
    if ove and UserLessonOverallModel.objects.filter(user_lesson__lesson=lesson,
                                                     user_lesson__user=user).exists() and not u.done:
        lab = UserTheoryLabModel.objects.filter(user=user, theory_lab__theory__lesson=lesson)
        tests = UserTestModel.objects.filter(user=user, test__lesson=lesson)
        lab_points = 0
        tests_points = 0
        for a in lab:
            lab_points += UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=a, enough=True).order_by(
                'created_at').last().points
        for b in tests:
            tests_points += UserAnsweredTestModel.objects.filter(user_test_model=b, enough=True).order_by(
                'created_at').last().points
        try:
            lab_points_end = lesson.lab_percentage * (lab_points / lab.count()) / 100
        except ZeroDivisionError:
            lab_points_end = 0
        try:
            tests_points_end = lesson.test_percentage * (tests_points / tests.count()) / 100
        except ZeroDivisionError:
            tests_points_end = 0
        ulo = get_object_or_404(UserLessonOverallModel, user_lesson=u)
        overall = tests_points_end + lab_points_end
        if timezone.now().date() > u.recommend_end_date and overall > 80:
            overall = 80
        UserGotLessonOverallModel.objects.update_or_create(user_overall=ulo, defaults={'points': overall})
        if not u.done and not u.end_time:
            u.end_time = timezone.now()
            u.complete_time = (u.end_time - u.start_time).total_seconds()
        u.done = True
        ulo.available = True
        ulo.save()
        u.save()
        ubm = get_object_or_404(UserBoughtCourseModel, user=user, course=lesson.course)
        g1 = 0
        g1o = 0
        g2 = 0
        g2o = 0
        for i in UserLessonModel.objects.filter(done=True, lesson__course=lesson.course, user=user):
            if TheoryLabChapterModel.objects.filter(theory__lesson=i.lesson, project=True).exists():
                g2 += UserGotLessonOverallModel.objects.get(user_overall__user_lesson=i).points
                g2o += 100
            else:
                g1 += UserGotLessonOverallModel.objects.get(user_overall__user_lesson=i).points
                g1o += 100
        if g1o == 0 and g2o > 0:
            gpa = round((g2 * 4 / g2o), 1)
        elif g2o == 0 and g1o > 0:
            gpa = round((g1 * 4 / g1o), 1)
        elif g1o > 0 and g2o > 0:
            non_plab = g1 * 4 / g1o
            plab = g2 * 4 / g2o
            gpa = round(((70 * non_plab / 100) + (30 * plab / 100)), 1)
        else:
            gpa = 0
        UserGPAHistory.objects.create(user_course=ubm, gpa=gpa)
        u.gpa = gpa
        ubm.gpa = gpa
        u.save()
        ubm.save()
        next_les = UserLessonModel.objects.filter(
            lesson=LessonModel.objects.filter(course=lesson.course, pk__gt=lesson.pk, active=True).order_by(
                'pk').first(), user=user).first()
        if next_les:
            if not next_les.done:
                next_les.activation_date = u.end_time.date() + relativedelta(days=next_les.lesson.activation_day)
                next_les.recommend_end_date = next_les.activation_date + relativedelta(
                    days=next_les.lesson.recommend_end)
                next_les.save()
                lesson_activate_new(next_les)
        else:
            ubm.end_time = timezone.now()
            ubm.complete_time = (ubm.end_time - ubm.start_time).total_seconds()
            ubm.completed = True
            ubm.save()


class EditorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorImageModel
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username')


class CourseForLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModel
        fields = ['id', 'title_lms', ]


class CourseListSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    def get_teacher_name(self, obj):
        if obj.teacher is not None:
            return obj.teacher.full_name
        else:
            return None

    def to_representation(self, instance):
        a = super(CourseListSerializer, self).to_representation(instance)
        user = self.context['request'].user
        if UserBoughtCourseModel.objects.filter(user=user, course=instance).exists():
            a['is_bought'] = True
        else:
            a['is_bought'] = False
        return a

    class Meta:
        model = CourseModel
        fields = ['id', 'title', 'title_lms', 'slug', 'teacher_name', 'image',
                  'image_lms', 'github', 'active']


class CourseDetailSerializer(serializers.ModelSerializer):
    learn = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    teacher_image = serializers.SerializerMethodField()
    teacher_id = serializers.SerializerMethodField()
    teacher_description = serializers.SerializerMethodField()
    mentors = serializers.SerializerMethodField()
    author = UserSerializer()

    def get_mentors(self, obj):
        if obj.mentor.exists():
            id_set = []
            for a in obj.mentor.all():
                id_set.append(a.user.id)
            return id_set
        else:
            return None

    def get_teacher_name(self, obj):
        if obj.teacher is not None:
            return obj.teacher.full_name
        else:
            return None

    def get_teacher_id(self, obj):
        if obj.teacher is not None:
            return obj.teacher.user.id
        else:
            return None

    def get_teacher_image(self, obj):
        if obj.teacher.image:
            return self.context['request'].build_absolute_uri(obj.teacher.image.url)
        else:
            return None

    def get_teacher_description(self, obj):
        if obj.teacher.description:
            return obj.teacher.description
        else:
            return None

    def get_learn(self, obj):
        return CourseTipsModelSerializer(CourseTipsModel.objects.filter(course=obj), many=True).data

    class Meta:
        model = CourseModel
        exclude = ['active', 'created_at', 'updated_at', 'image_course_title', 'image_teacher_title', 'teacher',
                   'mentor']
        depth = 1


class CourseTipsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTipsModel
        fields = '__all__'


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestModel
        exclude = ['processed', 'created_at']


class UserBoughtCourseCreateSerializer(serializers.ModelSerializer):
    click_trans_id = serializers.IntegerField(required=False)
    service_id = serializers.IntegerField(required=False)
    click_paydoc_id = serializers.IntegerField(required=False)
    merchant_trans_id = serializers.CharField(required=False)
    amount = serializers.IntegerField(required=False)
    action = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)
    course_id = serializers.IntegerField(required=False)
    error = serializers.IntegerField(required=False)
    error_note = serializers.CharField(required=False)
    sign_time = serializers.CharField(required=False)
    sign_string = serializers.CharField(required=False)
    merchant_prepare_id = serializers.CharField(required=False)
    merchant_confirm_id = serializers.CharField(required=False)

    def create(self, validated_data):
        user_id = self.context['user_id']
        course_id = self.context['course_id']
        user = get_object_or_404(UserModel, id=user_id)
        course = get_object_or_404(CourseModel, id=course_id)
        if UserBoughtCourseModel.objects.filter(user=user, course=course, trial=False).exists():
            raise ParseError("User already have this course")
        if ProfileModel.objects.get(user=user).permission == 0:
            ProfileModel.objects.filter(user=user).update(permission=1)
        if 'trial' in self.context and not self.context['trial']:
            ubm = get_object_or_404(UserBoughtCourseModel, user=user, course=course, trial=True)
            ubm.trial = False
            ubm.status = True
            ubm.expiration_date = timezone.now().date() + relativedelta(days=30)
            ubm.save()
            if UserLessonModel.objects.filter(user=user, lesson__course=course, lesson__active=True,
                                              available=True).exists():
                fl = UserLessonModel.objects.filter(user=user, lesson__course=course, lesson__active=True,
                                                    available=True).select_related('lesson').order_by(
                    'created_at').first()
                tla = sorted(list(UserTestModel.objects.filter(user=user, test__lesson=fl.lesson, done=True)) + list(
                    UserTheoryLabModel.objects.filter(user=user, theory_lab__theory__lesson=fl.lesson)),
                             key=lambda x: x.created_at)
                if tla and tla[-1].done:
                    next_les = UserLessonModel.objects.filter(user=user, lesson=LessonModel.objects.filter(
                        course=course, pk__gt=fl.lesson.pk, active=True).order_by('pk').first()).first()
                    if next_les:
                        if next_les.activation_date is None:
                            next_les.activation_date = fl.end_time.date() + relativedelta(days=fl.lesson.activation_day)
                        if next_les.recommend_end_date is None:
                            next_les.recommend_end_date = next_les.activation_date + relativedelta(
                                days=fl.lesson.recommend_end)
                        next_les.save()
                        lesson_activate_new(next_les)
                else:
                    if UserTheoryLabModel.objects.filter(theory_lab__theory__lesson=fl.lesson, user=user,
                                                         submitted=True).exists():
                        NotificationModel.objects.create(to_user=user, type=3)
                        for po in fl.lesson.course.mentor.all():
                            NotificationModel.objects.create(to_user=po.user, type=4, full_name=user.get_full_name(),
                                                             lesson=fl.lesson.title, course=course.title_lms)
            NotificationModel.objects.create(to_user=user, type=5, course=course.title_lms)
            error_response = {
                "error": 0,
                "error_note": "Success",
                "click_trans_id": self.context['click_trans_id'],
                "merchant_trans_id": self.context['merchant_trans_id'],
                "merchant_confirm_id": self.context['merchant_confirm_id'],
            }
            return error_response
        else:
            ubm = UserBoughtCourseModel.objects.create(course=course, user=user, status=True, trial=False,
                                                       bought_date=timezone.now().date(), start_time=timezone.now(),
                                                       expiration_date=timezone.now().date() + relativedelta(days=30))
        rep_att(ubm, course, user)
        NotificationModel.objects.create(to_user=user, type=5, course=course.title_lms)
        error_response = {
            "error": 0,
            "error_note": "Success",
            "click_trans_id": self.context['click_trans_id'],
            "merchant_trans_id": self.context['merchant_trans_id'],
            "merchant_confirm_id": self.context['merchant_confirm_id'],
        }
        return error_response

    class Meta:
        model = UserBoughtCourseModel
        exclude = ['bought_date', 'expiration_date', 'gpa', 'user', 'course', 'status', 'start_time', 'end_time',
                   'complete_time', 'trial', 'completed']


class UserAssignCourseCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = validated_data['user']
        course = validated_data['course']
        if UserBoughtCourseModel.objects.filter(user=user, course=course, trial=False).exists():
            raise ParseError("User already have this course")
        if ProfileModel.objects.get(user=user).permission == 0:
            ProfileModel.objects.filter(user=user).update(permission=1)
        if 'trial' in self.context and not self.context['trial']:
            ubm = get_object_or_404(UserBoughtCourseModel, user=user, course=course, trial=True)
            ubm.trial = False
            ubm.status = True
            ubm.expiration_date = timezone.now().date() + relativedelta(days=30)
            ubm.save()
            if UserLessonModel.objects.filter(user=user, lesson__course=course, lesson__active=True,
                                              available=True).exists():
                fl = UserLessonModel.objects.filter(user=user, lesson__course=course, lesson__active=True,
                                                    available=True).select_related('lesson').order_by(
                    'created_at').first()
                tla = sorted(list(UserTestModel.objects.filter(user=user, test__lesson=fl.lesson, done=True)) + list(
                    UserTheoryLabModel.objects.filter(user=user, theory_lab__theory__lesson=fl.lesson)),
                             key=lambda x: x.created_at)
                if tla and tla[-1].done:
                    next_les = UserLessonModel.objects.filter(user=user, lesson=LessonModel.objects.filter(
                        course=course, pk__gt=fl.lesson.pk, active=True).order_by('pk').first()).first()
                    if next_les:
                        next_les.activation_date = fl.end_time.date() + relativedelta(days=fl.lesson.activation_day)
                        next_les.recommend_end_date = next_les.activation_date + relativedelta(
                            days=fl.lesson.recommend_end)
                        next_les.save()
                        lesson_activate_new(next_les)
                else:
                    if UserTheoryLabModel.objects.filter(theory_lab__theory__lesson=fl.lesson, user=user,
                                                         submitted=True).exists():
                        NotificationModel.objects.create(to_user=user, type=3)
                        for po in fl.lesson.course.mentor.all():
                            NotificationModel.objects.create(to_user=po.user, type=4, full_name=user.get_full_name(),
                                                             lesson=fl.lesson.title, course=course.title_lms)
            NotificationModel.objects.create(to_user=user, type=5, course=course.title_lms)
            return validated_data
        else:
            ubm = UserBoughtCourseModel.objects.create(course=course, user=user, status=True, trial=False,
                                                       bought_date=timezone.now().date(), start_time=timezone.now(),
                                                       expiration_date=timezone.now().date() + relativedelta(days=30))
        rep_att(ubm, course, user)
        NotificationModel.objects.create(to_user=user, type=5, course=course.title_lms)
        return validated_data

    class Meta:
        model = UserBoughtCourseModel
        exclude = ['bought_date', 'expiration_date', 'gpa', 'status', 'start_time', 'end_time',
                   'complete_time', 'trial', 'completed']


class UserTrialCourseCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context['request'].user
        course = validated_data['course']
        if UserBoughtCourseModel.objects.filter(user=user, course=course, trial=False).exists():
            raise ParseError("User already have this course")
        if ProfileModel.objects.get(user=user).permission == 0:
            ProfileModel.objects.filter(user=user).update(permission=1)
        prof = get_object_or_404(ProfileModel, user=user)
        prof.used_trial = True
        prof.save()
        ubm = UserBoughtCourseModel.objects.create(course=course, user=user, status=True, trial=True,
                                                   bought_date=timezone.now().date(), start_time=timezone.now(),
                                                   expiration_date=timezone.now().date() + relativedelta(
                                                       days=30))
        rep_att(ubm, course, user)
        NotificationModel.objects.create(to_user=user, type=6, course=course.title_lms)
        validated_data['status'] = "Trial"
        return validated_data

    class Meta:
        model = UserBoughtCourseModel
        exclude = ['bought_date', 'expiration_date', 'user']


class UserBoughtCourseListSerializer(serializers.ModelSerializer):
    title_lms = serializers.CharField(source='course.title_lms')
    image_lms = serializers.ImageField(source='course.image_lms')

    def to_representation(self, instance):
        a = super(UserBoughtCourseListSerializer, self).to_representation(instance)
        user = self.context['request'].user
        all1 = UserLessonModel.objects.filter(lesson__course__userboughtcoursemodel=instance, user=user,
                                              lesson__active=True).count()
        down = UserLessonModel.objects.filter(lesson__course__userboughtcoursemodel=instance, user=user,
                                              lesson__active=True, done=True).count()
        a["all"] = all1
        a["completed"] = down
        try:
            a["percentage"] = round(down * 100 / all1, 2)
        except ZeroDivisionError:
            a["percentage"] = 0
        return a

    class Meta:
        model = UserBoughtCourseModel
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackModel
        exclude = ['id']


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherModel
        fields = '__all__'


class SliderChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderChildModel
        fields = ['id', 'title', 'description']


class SliderSerializer(serializers.ModelSerializer):
    children = SliderChildSerializer(many=True)

    class Meta:
        model = SliderMainModel
        fields = ['title', 'image', 'children']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagModel
        fields = ['id', 'tag']


class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherModel
        fields = ['id', 'full_name', 'image', 'description']


class CourseCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)
    image_course_title = serializers.CharField(required=False)
    image_teacher_title = serializers.CharField(required=False)
    tag = TagSerializer(many=True, read_only=True)
    tags = serializers.ListField(required=False, write_only=True)
    mentor = MentorSerializer(many=True, read_only=True)
    mentors = serializers.ListField(write_only=True, required=False)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['slug'] = slugify(validated_data['title'])
        exist = False
        exist2 = False
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            tags = tags[0]
            exist = True
        if 'mentors' in validated_data:
            mentors = validated_data.pop('mentors')
            mentors = mentors[0]
            exist2 = True
        vnv = super(CourseCreateSerializer, self).create(validated_data)
        if exist:
            for a in tags:
                if a.isdigit() and TagModel.objects.filter(id=a).exists():
                    vnv.tag.add(a)
        if exist2:
            for b in mentors:
                if b.isdigit() and TeacherModel.objects.filter(user_id=b).exists():
                    vnv.mentor.add(TeacherModel.objects.get(user_id=b).id)
        vnv.mentor.add(validated_data['teacher'])
        if vnv.active:
            for b in UserModel.objects.filter(profile__permission=3):
                if not UserBoughtCourseModel.objects.filter(user=b, course=vnv).exists():
                    admin_attach(course=vnv, user=b)
                else:
                    UserBoughtCourseModel.objects.filter(user=b, course=vnv).update(
                        expiration_date=timezone.now() + relativedelta(years=1000))
            for d in UserModel.objects.filter(profile__permission=2):
                if not UserBoughtCourseModel.objects.filter(user=d, course=vnv).exists() and CourseModel.objects.filter(
                        mentor__user=d).exists():
                    admin_attach(course=vnv, user=d)
                elif UserBoughtCourseModel.objects.filter(user=d, course=vnv).exists() and CourseModel.objects.filter(
                        mentor__user=d).exists():
                    UserBoughtCourseModel.objects.filter(user=d, course=vnv).update(
                        expiration_date=timezone.now() + relativedelta(years=1000))
        return vnv

    def update(self, instance, validated_data):
        if 'mentors' in validated_data:
            instance.mentor.clear()
            for a in validated_data['mentors'][0]:
                if a.isdigit() and TeacherModel.objects.filter(user_id=a).exists():
                    instance.mentor.add(TeacherModel.objects.get(user_id=a).id)
            instance.mentor.add(instance.teacher.id)
        if 'tags' in validated_data:
            instance.tag.clear()
            for a in validated_data['tags'][0]:
                if a.isdigit() and TagModel.objects.filter(id=a).exists():
                    instance.tag.add(a)
        end = super(CourseCreateSerializer, self).update(instance, validated_data)
        if end.active:
            for b in UserModel.objects.filter(profile__permission=3):
                if not UserBoughtCourseModel.objects.filter(user=b, course=end).exists():
                    admin_attach(course=end, user=b)
                else:
                    UserBoughtCourseModel.objects.filter(user=b, course=end).update(
                        expiration_date=timezone.now() + relativedelta(years=1000))
            for d in UserModel.objects.filter(profile__permission=2):
                if not UserBoughtCourseModel.objects.filter(user=d, course=end).exists() and CourseModel.objects.filter(
                        mentor__user=d).exists():
                    admin_attach(course=end, user=d)
                elif UserBoughtCourseModel.objects.filter(user=d, course=end).exists() and CourseModel.objects.filter(
                        mentor__user=d).exists():
                    UserBoughtCourseModel.objects.filter(user=d, course=end).update(
                        expiration_date=timezone.now() + relativedelta(years=1000))
        return end

    class Meta:
        model = CourseModel
        fields = '__all__'
        read_only_fields = ['author']


class LessonListSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, obj):
        return LessonSerializer(LessonModel.objects.filter(course=obj).order_by('created_at'), many=True,
                                context=self.context).data

    class Meta:
        model = CourseModel
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    course = CourseForLessonSerializer()
    author = UserSerializer()

    class Meta:
        model = LessonModel
        fields = '__all__'


class LessonCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if validated_data['lab_percentage'] + validated_data['test_percentage'] != 100:
            raise ParseError("Sum of percentages should be equal to 100")
        course = validated_data['course']
        if validated_data['recommend_end'] < 7:
            raise ParseError("Recommend end day should be at least 7 days")
        lesson = super(LessonCreateSerializer, self).create(validated_data)
        ad = validated_data['activation_day']
        ed = validated_data['recommend_end']
        for a in UserBoughtCourseModel.objects.select_related('user').filter(course=course):
            if LessonModel.objects.filter(course=course).count() == 1:
                if ad == 0:
                    if a.trial:
                        UserLessonModel.objects.create(lesson=lesson, user=a.user, available=False, done=False,
                                                       activation_date=timezone.now().date(),
                                                       recommend_end_date=timezone.now().date() + relativedelta(
                                                           days=int(ed)))
                    else:
                        UserLessonModel.objects.create(lesson=lesson, user=a.user, available=True, done=False,
                                                       activation_date=timezone.now().date(),
                                                       recommend_end_date=timezone.now().date() + relativedelta(
                                                           days=int(ed)))
                else:
                    activation_date = a.bought_date + relativedelta(days=int(ad))
                    if activation_date <= timezone.datetime.now().date() and not a.trial:
                        UserLessonModel.objects.create(lesson=lesson, user=a.user, available=True, done=False,
                                                       activation_date=activation_date,
                                                       recommend_end_date=activation_date + relativedelta(days=int(ed)))
                    else:
                        UserLessonModel.objects.create(lesson=lesson, user=a.user, available=False, done=False,
                                                       activation_date=activation_date,
                                                       recommend_end_date=activation_date + relativedelta(days=int(ed)))
            else:
                l1 = LessonModel.objects.filter(course=course, pk__lt=lesson.pk).order_by('-pk').first()
                if UserLessonModel.objects.filter(lesson=l1, user=a.user, done=True).exists():
                    if ad == 0:
                        if a.trial:
                            UserLessonModel.objects.create(lesson=lesson, user=a.user, available=False, done=False,
                                                           activation_date=timezone.now().date(),
                                                           recommend_end_date=timezone.now().date() + relativedelta(
                                                               days=int(ed)))
                        else:
                            UserLessonModel.objects.create(lesson=lesson, user=a.user, available=True, done=False,
                                                           activation_date=timezone.now().date(),
                                                           recommend_end_date=timezone.now().date() + relativedelta(
                                                               days=int(ed)))
                    else:
                        u1 = UserLessonModel.objects.get(lesson=l1, user=a.user)
                        activation_date = u1.end_time.date() + relativedelta(days=int(ad))
                        if activation_date <= timezone.datetime.now().date() and not a.trial:
                            UserLessonModel.objects.create(lesson=lesson, user=a.user, available=True, done=False,
                                                           activation_date=u1.end_time + relativedelta(days=int(ad)),
                                                           recommend_end_date=u1.end_time + relativedelta(
                                                               days=int(ad)) + relativedelta(days=int(ed)))
                        else:
                            UserLessonModel.objects.create(lesson=lesson, user=a.user, available=False, done=False,
                                                           activation_date=u1.end_time + relativedelta(days=int(ad)),
                                                           recommend_end_date=u1.end_time + relativedelta(
                                                               days=int(ad)) + relativedelta(days=int(ed)))
                else:
                    if ad == 0:
                        UserLessonModel.objects.create(lesson=lesson, user=a.user, available=False, done=False,
                                                       activation_date=timezone.now().date(),
                                                       recommend_end_date=timezone.now().date() + relativedelta(
                                                           days=int(ed)))
                    else:
                        UserLessonModel.objects.create(lesson=lesson, user=a.user, available=False, done=False)
            if lesson.active:
                NotificationModel.objects.create(to_user=a.user, type=7, lesson=lesson.title, course=course.title_lms)
        return lesson

    def update(self, instance, validated_data):
        ll = super(LessonCreateSerializer, self).update(instance, validated_data)
        if 'active' in validated_data and validated_data['active']:
            for a in UserBoughtCourseModel.objects.filter(course=instance.course).select_related('user'):
                ylm = UserLessonModel.objects.filter(pk__lt=instance.pk, user=a.user, lesson__course=a.course,
                                                     lesson__active=True).order_by('-pk')
                if ylm.exists():
                    pv = ylm.first()
                    if pv.done:
                        if (pv.end_time.date() + relativedelta(days=pv.lesson.activation_day)) <= timezone.now().date():
                            UserLessonModel.objects.filter(user=a.user, lesson=instance).update(
                                activation_date=pv.end_time.date() + relativedelta(days=pv.lesson.activation_day))
                            lesson_activate_new(UserLessonModel.objects.get(user=a.user, lesson=instance))
                        else:
                            UserLessonModel.objects.filter(user=a.user, lesson=instance).update(
                                activation_date=pv.end_time.date() + relativedelta(days=pv.lesson.activation_day))
        return ll

    class Meta:
        model = LessonModel
        fields = '__all__'
        read_only_fields = ['author']


class LessonDetailSerializer(serializers.ModelSerializer):
    theories_and_tests = serializers.SerializerMethodField('get_inside')
    author = UserSerializer(read_only=True)

    def get_inside(self, obj):
        data = []
        all1 = sorted(list(TheoryModel.objects.filter(lesson=obj)) + list(TestModel.objects.filter(lesson=obj)),
                      key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "TheoryModel":
                th = TheorySerializer(a, many=False, context=self.context).data
                th['type'] = "Theory"
                data.append(th)
            elif a.__class__.__name__ == "TestModel":
                te = TestCreateSerializer(a, many=False, context=self.context).data
                te['type'] = "Test"
                data.append(te)
        return data

    class Meta:
        model = LessonModel
        fields = '__all__'


class TheorySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if (TheoryModel.objects.filter(lesson=validated_data['lesson']).count() + TestModel.objects.filter(
                lesson=validated_data['lesson']).count()) == 0:
            avail = True
        else:
            avail = False
        t = super(TheorySerializer, self).create(validated_data)
        t1 = False
        if not avail:
            all1 = sorted(list(TheoryModel.objects.filter(lesson=validated_data['lesson'])) + list(
                TestModel.objects.filter(lesson=validated_data['lesson'])), key=lambda x: x.created_at)
            ind = all1.index(t) - 1
            if index_in_list(all1, ind) and len(all1) > 1:
                t1 = True
                if all1[ind].__class__.__name__ == "TheoryModel":
                    th = True
                    t2 = all1[ind]
                elif all1[ind].__class__.__name__ == "TestModel":
                    th = False
                    t2 = all1[ind]
        for a in UserBoughtCourseModel.objects.filter(course__lesson=validated_data['lesson']).select_related('user'):
            if UserLessonModel.objects.filter(user=a.user, lesson=validated_data['lesson'],
                                              available=True).exists():
                if t1 and th:
                    if UserTheoryModel.objects.filter(done=True, user=a.user, theory=t2).exists():
                        avail = True
                    else:
                        avail = False
                elif t1 and not th:
                    if UserTestModel.objects.filter(test=t2, user=a.user, done=True).exists():
                        avail = True
                    else:
                        avail = False
                elif not t1:
                    avail = True
            else:
                avail = False
            UserTheoryModel.objects.create(available=avail, user=a.user, theory=t)
        return t

    class Meta:
        model = TheoryModel
        fields = '__all__'
        read_only_fields = ['author']


class TheoryDetailSerializer(serializers.ModelSerializer):
    intro = serializers.SerializerMethodField()
    chapters_and_labs = serializers.SerializerMethodField()

    def get_intro(self, obj):
        if TheoryIntroModel.objects.filter(theory=obj).exists():
            return TheoryIntroCreateSerializer(TheoryIntroModel.objects.get(theory=obj), many=False,
                                               context=self.context).data
        else:
            return None

    def get_chapters_and_labs(self, obj):
        data = []
        all1 = sorted(list(TheoryChapterModel.objects.filter(theory=obj)) + list(
            TheoryLabChapterModel.objects.filter(theory=obj)), key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if all1.index(a) == len(all1) - 1:
                is_end = True
            else:
                is_end = False
            if a.__class__.__name__ == "TheoryChapterModel":
                th = TheoryChapterCreateSerializer(a, many=False, context=self.context).data
                th["is_end"] = is_end
                data.append(th)
            elif a.__class__.__name__ == "TheoryLabChapterModel":
                th = TheoryLabCreateSerializer(a, many=False, context=self.context).data
                th["is_end"] = is_end
                data.append(th)
        return data

    class Meta:
        model = TheoryModel
        fields = '__all__'


class TheoryIntroCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        t = super(TheoryIntroCreateSerializer, self).create(validated_data)
        for a in UserBoughtCourseModel.objects.filter(course__lesson__theory=validated_data['theory']).select_related(
                'user'):
            if UserTheoryModel.objects.filter(theory=validated_data['theory'], user=a.user,
                                              available=True).exists():
                avail = True
            else:
                avail = False
            UserTheoryIntroModel.objects.create(available=avail, user=a.user, theory_intro=t)
        return t

    def to_representation(self, instance):
        a = super(TheoryIntroCreateSerializer, self).to_representation(instance)
        a['type'] = 'Theory Intro'
        return a

    class Meta:
        model = TheoryIntroModel
        fields = '__all__'
        read_only_fields = ['author', 'id']


class TheoryChapterCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        theory = validated_data['theory']
        if not TheoryIntroModel.objects.filter(theory=validated_data['theory']).exists():
            raise ParseError("Create theory intro first")
        t = super(TheoryChapterCreateSerializer, self).create(validated_data)
        for a in UserBoughtCourseModel.objects.filter(course__lesson__theory=theory).select_related('user'):
            if UserTheoryIntroModel.objects.filter(user=a.user, done=True, theory_intro__theory=theory).exists():
                all1 = sorted(list(TheoryChapterModel.objects.filter(theory=theory)) + list(
                    TheoryLabChapterModel.objects.filter(theory=theory)), key=lambda x: x.created_at)
                if len(all1) > 1:
                    pev = all1[all1.index(t) - 1]
                    if pev.__class__.__name__ == "TheoryChapterModel":
                        done = UserTheoryChapterModel.objects.get(user=a.user, theory_chapter=pev).done
                    elif pev.__class__.__name__ == "TheoryLabChapterModel":
                        done = UserTheoryLabModel.objects.get(user=a.user, theory_lab=pev).done
                    UserTheoryChapterModel.objects.create(available=done, user=a.user, theory_chapter=t)
                else:
                    UserTheoryChapterModel.objects.create(available=True, user=a.user, theory_chapter=t)
            else:
                UserTheoryChapterModel.objects.create(available=False, user=a.user, theory_chapter=t)
        return t

    def to_representation(self, instance):
        a = super(TheoryChapterCreateSerializer, self).to_representation(instance)
        a['type'] = 'Theory Chapter'
        return a

    class Meta:
        model = TheoryChapterModel
        fields = '__all__'
        read_only_fields = ['author', 'id']


class TheoryLabCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    project = serializers.BooleanField(required=True)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if not validated_data['control'] and 'minimum_points' not in validated_data:
            raise ParseError("Send minimum points when control is False")
        theory = validated_data['theory']
        if not TheoryIntroModel.objects.filter(theory=validated_data['theory']).exists():
            raise ParseError("Create theory intro first")
        if validated_data['type'] == 0:
            if 'embed' not in validated_data:
                raise ParseError("Send replit link")
            if TheoryLabChapterModel.objects.filter(
                    theory__lesson__course=theory.lesson.course).count() == 0 and 'trial' not in validated_data:
                raise ParseError("Send replit trial link for first lab")
        t = super(TheoryLabCreateSerializer, self).create(validated_data)
        for a in UserBoughtCourseModel.objects.filter(course__lesson__theory=theory).select_related('user'):
            if UserTheoryIntroModel.objects.filter(user=a.user, done=True, theory_intro__theory=theory).exists():
                all1 = sorted(list(TheoryChapterModel.objects.filter(theory=theory)) + list(
                    TheoryLabChapterModel.objects.filter(theory=theory)), key=lambda x: x.created_at)
                if len(all1) > 1:
                    pev = all1[all1.index(t) - 1]
                    if pev.__class__.__name__ == "TheoryChapterModel":
                        done = UserTheoryChapterModel.objects.get(user=a.user, theory_chapter=pev).done
                    elif pev.__class__.__name__ == "TheoryLabChapterModel":
                        done = UserTheoryLabModel.objects.get(user=a.user, theory_lab=pev).done
                    UserTheoryLabModel.objects.create(available=done, user=a.user, theory_lab=t)
                else:
                    UserTheoryLabModel.objects.create(available=True, user=a.user, theory_lab=t)
            else:
                UserTheoryLabModel.objects.create(available=False, user=a.user, theory_lab=t)
            ul = UserLessonModel.objects.get(lesson__theory=theory, user=a.user)
            if not UserLessonOverallModel.objects.filter(user_lesson=ul).exists():
                UserLessonOverallModel.objects.create(user_lesson=ul)
        return t

    def to_representation(self, instance):
        a = super(TheoryLabCreateSerializer, self).to_representation(instance)
        a['type'] = 'Theory Lab'
        return a

    class Meta:
        model = TheoryLabChapterModel
        fields = '__all__'
        read_only_fields = ['author']


class TestCreateSerializer(serializers.ModelSerializer):
    control = serializers.BooleanField(required=True)
    author = UserSerializer(read_only=True)

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        lesson = validated_data['lesson']
        if (TheoryModel.objects.filter(lesson=lesson).count() + TestModel.objects.filter(lesson=lesson).count()) == 0:
            avail = True
        else:
            avail = False
        if not validated_data['control'] and 'minimum_percentage' not in validated_data:
            raise ParseError("Send minimum percentage when control is False")
        t = super(TestCreateSerializer, self).create(validated_data)
        t1 = False
        if not avail:
            all1 = sorted(
                list(TheoryModel.objects.filter(lesson=lesson)) + list(TestModel.objects.filter(lesson=lesson)),
                key=lambda x: x.created_at)
            ind = all1.index(t) - 1
            if index_in_list(all1, ind) and len(all1) > 1:
                t1 = True
                if all1[ind].__class__.__name__ == "TheoryModel":
                    th = True
                    t2 = all1[ind]
                elif all1[ind].__class__.__name__ == "TestModel":
                    th = False
                    t2 = all1[ind]
        for a in UserBoughtCourseModel.objects.filter(course__lesson=lesson).select_related('user'):
            ul = UserLessonModel.objects.get(user=a.user, lesson=lesson)
            if ul.available and t1:
                if th:
                    if UserTheoryModel.objects.filter(done=True, user=a.user, theory=t2).exists():
                        avail = True
                    else:
                        avail = False
                elif not th:
                    if UserTestModel.objects.filter(test=t2, user=a.user, done=True).exists():
                        avail = True
                    else:
                        avail = False
            elif ul.available and not t1:
                avail = True
            else:
                avail = False
            UserTestModel.objects.create(available=avail, user=a.user, test=t)
        return t

    class Meta:
        model = TestModel
        fields = '__all__'
        read_only_fields = ['author', 'id']


class TestDetailSerializer(serializers.ModelSerializer):
    intro = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()

    def get_intro(self, obj):
        if TestIntroModel.objects.filter(test=obj).exists():
            return TestIntroCreateSerializer(TestIntroModel.objects.get(test=obj), many=False,
                                             context=self.context).data
        else:
            return None

    def get_chapters(self, obj):
        if TestChapterModel.objects.filter(test=obj).exists():
            return TestChapterCreateSerializer(TestChapterModel.objects.filter(test=obj).order_by('created_at'),
                                               many=True, context=self.context).data
        else:
            return None

    class Meta:
        model = TestModel
        fields = '__all__'
        read_only_fields = ['author', 'id']


class TestIntroCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        t = super(TestIntroCreateSerializer, self).create(validated_data)
        for a in UserBoughtCourseModel.objects.filter(course__lesson__test=validated_data['test']).select_related(
                'user'):
            if UserTestModel.objects.filter(test=validated_data['test'], user=a.user, available=True).exists():
                avail = True
            else:
                avail = False
            UserTestIntroModel.objects.create(available=avail, user=a.user, test_intro=t)
        return t

    def to_representation(self, instance):
        a = super(TestIntroCreateSerializer, self).to_representation(instance)
        a['type'] = 'Test Intro'
        return a

    class Meta:
        model = TestIntroModel
        fields = '__all__'
        read_only_fields = ['author', 'id']


class TestChapterCreateSerializer(serializers.ModelSerializer):
    variants = serializers.JSONField(required=False)
    all_variants = serializers.SerializerMethodField('get_all')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if not TestIntroModel.objects.filter(test=validated_data['test']).exists():
            raise ParseError("Create test intro first")
        if validated_data['type'] != 2 and 'variants' not in validated_data:
            raise ParseError("Send variants")
        if validated_data['type'] == 2 and 'short_answer' not in validated_data:
            raise ParseError("Send short answer")
        if 'variants' in validated_data:
            variants = validated_data.pop('variants')
        else:
            variants = None
        t = super(TestChapterCreateSerializer, self).create(validated_data)
        for a in UserBoughtCourseModel.objects.filter(course__lesson__test=validated_data['test']).select_related(
                'user'):
            ul = UserLessonModel.objects.get(user=a.user, lesson=t.test.lesson)
            UserTestChapterModel.objects.create(available=False, test_chapter=t, user=a.user)
            if not UserLessonOverallModel.objects.filter(user_lesson=ul).exists():
                UserLessonOverallModel.objects.create(user_lesson=ul)
        if t.type != 2 and variants is not None:
            for b in variants:
                TestVariantModel.objects.create(test_chapter=t, variant=b['variant'], answer=b['answer'])
        return t

    def update(self, instance, validated_data):
        t = super(TestChapterCreateSerializer, self).update(instance, validated_data)
        if 'variants' in validated_data:
            variants = validated_data.pop('variants')
        else:
            variants = None
        if t.type != 2 and variants is not None:
            tvm = TestVariantModel.objects.filter(test_chapter=t)
            for a in variants:
                if 'id' in a:
                    TestVariantModel.objects.filter(id=a['id'], test_chapter=t).update(variant=a['variant'],
                                                                                       answer=a['answer'])
                    tvm = tvm.exclude(id=a['id'])
                else:
                    newtvm = TestVariantModel.objects.create(test_chapter=t, variant=a['variant'], answer=a['answer'])
                    tvm = tvm.exclude(id=newtvm.id)
            tvm.delete()
        return t

    def get_all(self, obj):
        return TestVariantSerializer(TestVariantModel.objects.filter(test_chapter=obj), many=True).data

    def to_representation(self, instance):
        a = super(TestChapterCreateSerializer, self).to_representation(instance)
        a['test_type'] = instance.type
        a['type'] = 'Test Chapter'
        return a

    class Meta:
        model = TestChapterModel
        fields = '__all__'
        read_only_fields = ['author', 'id']


class TestVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestVariantModel
        fields = '__all__'


class StudentLessonSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()

    class Meta:
        model = UserLessonModel
        fields = '__all__'


class StudentLessonDetailSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()
    theories_and_tests = serializers.SerializerMethodField('get_inside')
    overall = serializers.SerializerMethodField()

    def get_overall(self, obj):
        if UserLessonOverallModel.objects.filter(user_lesson=obj).exists():
            return StudentOverallSerializer(UserLessonOverallModel.objects.get(user_lesson=obj), many=False,
                                            context=self.context).data
        else:
            return None

    def get_inside(self, obj):
        data = []
        lesson = get_object_or_404(LessonModel, userlessonmodel=obj)
        all1 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=lesson, user=obj.user)) + list(
            UserTestModel.objects.filter(test__lesson=lesson, user=obj.user)), key=lambda x: x.created_at)
        if not all1:
            return None
        for a in all1:
            if a.__class__.__name__ == "UserTheoryModel":
                data.append(StudentTheorySerializer(a, many=False, context=self.context).data)
            elif a.__class__.__name__ == "UserTestModel":
                data.append(StudentTestSerializer(a, many=False, context=self.context).data)
        return data

    class Meta:
        model = UserLessonModel
        fields = '__all__'


class StudentTheorySerializer(serializers.ModelSerializer):
    theory = TheorySerializer()

    def to_representation(self, instance):
        a = super(StudentTheorySerializer, self).to_representation(instance)
        user = instance.user
        theory = instance.theory
        intros = UserTheoryIntroModel.objects.filter(user=user, theory_intro__theory=theory)
        chapters = UserTheoryChapterModel.objects.filter(user=user, theory_chapter__theory=theory)
        labs = UserTheoryLabModel.objects.filter(user=user, theory_lab__theory=theory)
        all1 = intros.count() + chapters.count() + labs.count()
        down = intros.filter(done=True).count() + chapters.filter(done=True).count() + labs.filter(done=True).count()
        a["all"] = all1
        a["completed"] = down
        try:
            a["percentage"] = round(down * 100 / all1, 2)
        except ZeroDivisionError:
            a["percentage"] = 0
        if labs.filter(seen=True).exists():
            last_lab = labs.filter(seen=True).order_by('created_at').last()
            if last_lab.done:
                a['lab_check'] = None
            else:
                if last_lab.again:
                    a['lab_check'] = False
                elif last_lab.submitted:
                    a['lab_check'] = True
                else:
                    a['lab_check'] = None
        else:
            a['lab_check'] = None
        return a

    class Meta:
        model = UserTheoryModel
        fields = '__all__'


class StudentTheoryDetailSerializer(serializers.ModelSerializer):
    theory = TheorySerializer()
    intro = serializers.SerializerMethodField()
    chapters_and_labs = serializers.SerializerMethodField()

    def get_intro(self, obj):
        if UserTheoryIntroModel.objects.filter(
                theory_intro__in=TheoryIntroModel.objects.filter(theory=obj.theory),
                user=self.context['request'].user).exists():
            return StudentTheoryIntroSerializer(
                UserTheoryIntroModel.objects.get(theory_intro=TheoryIntroModel.objects.get(theory=obj.theory),
                                                 user=self.context['request'].user), many=False,
                context=self.context).data
        else:
            return None

    def get_chapters_and_labs(self, obj):
        data = []
        all1 = sorted(
            list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=obj.theory, user=obj.user)) + list(
                UserTheoryLabModel.objects.filter(theory_lab__theory=obj.theory, user=obj.user)),
            key=lambda x: x.created_at)
        if not all1:
            return []
        for a in all1:
            if a.__class__.__name__ == "UserTheoryChapterModel":
                th = StudentTheoryChapterSerializer(a, many=False, context=self.context).data
                data.append(th)
            elif a.__class__.__name__ == "UserTheoryLabModel":
                th = StudentTheoryLabSerializer(a, many=False, context=self.context).data
                data.append(th)
        return data

    def to_representation(self, instance):
        a = super(StudentTheoryDetailSerializer, self).to_representation(instance)
        a['lesson'] = get_object_or_404(UserLessonModel, user=instance.user, lesson=instance.theory.lesson).id
        return a

    class Meta:
        model = UserTheoryModel
        fields = '__all__'


class StudentTheoryIntroSerializer(serializers.ModelSerializer):
    theory_intro = TheoryIntroCreateSerializer()

    def update(self, instance, validated_data):
        if "done" in validated_data and validated_data['done'] and not instance.done:
            user = instance.user
            if not instance.seen:
                raise ParseError("You must see it")
            theory = instance.theory_intro.theory
            all2 = sorted(
                list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=theory, user=instance.user)) + list(
                    UserTheoryLabModel.objects.filter(theory_lab__theory=theory, user=instance.user)),
                key=lambda x: x.created_at)
            if len(all2) > 0:
                all2[0].available = True
                all2[0].save()
            else:
                utm = get_object_or_404(UserTheoryModel, user=user, theory=theory)
                if not utm.done and not utm.end_time:
                    utm.end_time = timezone.now()
                    utm.complete_time = (utm.end_time - utm.start_time).total_seconds()
                utm.done = True
                utm.save()
                lesson = theory.lesson
                all1 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=lesson, user=user)) + list(
                    UserTestModel.objects.filter(test__lesson=lesson, user=user)), key=lambda x: x.created_at)
                ind = all1.index(utm) + 1
                if index_in_list(all1, ind):
                    unlock_next(all1, ind, instance)
                else:
                    if not UserLessonOverallModel.objects.filter(
                            user_lesson=UserLessonModel.objects.get(lesson=lesson, user=user)).exists():
                        ulm = get_object_or_404(UserLessonModel, lesson=lesson, user=user)
                        if not ulm.done:
                            ulm.done = True
                        if not ulm.end_time:
                            ulm.end_time = timezone.now()
                            ulm.complete_time = (ulm.end_time - ulm.start_time).total_seconds()
                        ulm.save()
                        next_les = UserLessonModel.objects.filter(user=user, lesson=LessonModel.objects.filter(
                            course=lesson.course, pk__gt=lesson.pk, active=True).order_by('pk').first()).first()
                        if next_les:
                            if not next_les.done:
                                next_les.activation_date = ulm.end_time.date() + relativedelta(
                                    days=lesson.activation_day)
                                next_les.recommend_end_date = next_les.activation_date + relativedelta(
                                    days=lesson.recommend_end)
                                next_les.save()
                                lesson_activate_new(next_les)
                        else:
                            ubm = get_object_or_404(UserBoughtCourseModel, user=user, course=lesson.course)
                            ubm.end_time = timezone.now()
                            ubm.complete_time = (ubm.end_time - ubm.start_time).total_seconds()
                            ubm.completed = True
                            ubm.save()
                    else:
                        count_points(lesson, instance.user)
        return super(StudentTheoryIntroSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        a = super(StudentTheoryIntroSerializer, self).to_representation(instance)
        user = instance.user
        theory = instance.theory_intro.theory
        all1 = sorted(list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=theory, user=user)) + list(
            UserTheoryLabModel.objects.filter(theory_lab__theory=theory, user=user)), key=lambda x: x.created_at)
        if all1:
            a['is_end'] = False
        else:
            a['is_end'] = True
        if UserBoughtCourseModel.objects.get(user=user, course=theory.lesson.course).trial:
            ulm = get_object_or_404(UserLessonModel, user=user, lesson=theory.lesson)
            utm = get_object_or_404(UserTheoryModel, user=user, theory=theory)
            all2 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=theory.lesson, user=user)) + list(
                UserTestModel.objects.filter(test__lesson=theory.lesson, user=user)), key=lambda x: x.created_at)
            if not all1 and all2[-1] == utm and UserLessonModel.objects.filter(user=user,
                                                                               lesson__course=theory.lesson.course).order_by(
                'created_at').first() == ulm:
                a['is_trial'] = True
            else:
                a['is_trial'] = False
        return a

    class Meta:
        model = UserTheoryIntroModel
        fields = '__all__'
        read_only_fields = ['theory_intro', 'user', 'available', 'seen']


class StudentTheoryChapterSerializer(serializers.ModelSerializer):
    theory_chapter = TheoryChapterCreateSerializer()

    def update(self, instance, validated_data):
        if "done" in validated_data and validated_data["done"] and not instance.done:
            if not instance.seen:
                raise ParseError("You must see it")
            if not instance.done and not instance.end_time:
                instance.end_time = timezone.now()
                instance.complete_time = (instance.end_time - instance.start_time).total_seconds()
                instance.save()
            user = instance.user
            theory = instance.theory_chapter.theory
            all2 = sorted(
                list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=theory, user=user)) + list(
                    UserTheoryLabModel.objects.filter(theory_lab__theory=theory, user=user)),
                key=lambda x: x.created_at)
            ind = all2.index(instance) + 1
            if index_in_list(all2, ind):
                all2[ind].available = True
                all2[ind].save()
            else:
                utm = get_object_or_404(UserTheoryModel, user=user, theory=theory)
                if not utm.done:
                    utm.done = True
                if not utm.end_time:
                    utm.end_time = timezone.now()
                    utm.complete_time = (utm.end_time - utm.start_time).total_seconds()
                utm.save()
                lesson = theory.lesson
                all1 = sorted(
                    list(UserTheoryModel.objects.filter(theory__lesson=lesson, user=user)) + list(
                        UserTestModel.objects.filter(test__lesson=lesson, user=user)), key=lambda x: x.created_at)
                ind = all1.index(utm) + 1
                if index_in_list(all1, ind):
                    unlock_next(all1, ind, instance)
                else:
                    if not UserLessonOverallModel.objects.filter(
                            user_lesson=UserLessonModel.objects.get(lesson=lesson, user=instance.user)).exists():
                        ulm = get_object_or_404(UserLessonModel, lesson=lesson, user=instance.user)
                        if not ulm.done:
                            ulm.done = True
                        if not ulm.end_time:
                            ulm.end_time = timezone.now()
                            ulm.complete_time = (ulm.end_time - ulm.start_time).total_seconds()
                        ulm.save()
                        next_les = UserLessonModel.objects.filter(user=user, lesson=LessonModel.objects.filter(
                            course=lesson.course, pk__gt=lesson.pk, active=True).order_by('pk').first()).first()
                        if next_les:
                            if not next_les.done:
                                next_les.activation_date = ulm.end_time.date() + relativedelta(
                                    days=lesson.activation_day)
                                next_les.recommend_end_date = next_les.activation_date + relativedelta(
                                    days=lesson.recommend_end)
                                next_les.save()
                                lesson_activate_new(next_les)
                        else:
                            ubm = get_object_or_404(UserBoughtCourseModel, user=user, course=lesson.course)
                            ubm.end_time = timezone.now()
                            ubm.complete_time = (ubm.end_time - ubm.start_time).total_seconds()
                            ubm.completed = True
                            ubm.save()
                    else:
                        count_points(lesson, instance.user)
        t = super(StudentTheoryChapterSerializer, self).update(instance, validated_data)
        return t

    def to_representation(self, instance):
        a = super(StudentTheoryChapterSerializer, self).to_representation(instance)
        user = instance.user
        theory = instance.theory_chapter.theory
        all1 = sorted(list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=theory, user=user)) + list(
            UserTheoryLabModel.objects.filter(theory_lab__theory=theory, user=user)), key=lambda x: x.created_at)
        if all1.index(instance) == len(all1) - 1:
            a['is_end'] = True
        else:
            a['is_end'] = False
        if UserBoughtCourseModel.objects.get(user=user, course=theory.lesson.course).trial:
            all2 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=theory.lesson, user=user)) + list(
                UserTestModel.objects.filter(test__lesson=theory.lesson, user=user)), key=lambda x: x.created_at)
            ulm = get_object_or_404(UserLessonModel, user=user, lesson=theory.lesson)
            utm = get_object_or_404(UserTheoryModel, user=user, theory=theory)
            if all2[-1] == utm and UserLessonModel.objects.filter(user=user,
                                                                  lesson__course=theory.lesson.course).order_by(
                'created_at').first() == ulm and a['is_end']:
                a['is_trial'] = True
            else:
                a['is_trial'] = False
        return a

    class Meta:
        model = UserTheoryChapterModel
        fields = '__all__'
        read_only_fields = ['theory_chapter', 'user', 'available', 'seen']


class StudentTheoryLabAnsweredSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnsweredTheoryLabModel
        fields = '__all__'


class StudentTheoryLabSerializer(serializers.ModelSerializer):
    theory_lab = TheoryLabCreateSerializer()
    answered = serializers.SerializerMethodField()
    github = serializers.CharField(required=False)

    def get_answered(self, obj):
        if UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=obj).exists():
            return StudentTheoryLabAnsweredSerializer(
                UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=obj).order_by('created_at'), many=True,
                context=self.context).data
        else:
            return []

    def update(self, instance, validated_data):
        if 'submitted' in validated_data and validated_data['submitted']:
            if not instance.seen:
                raise ParseError("It is not seen")
            if instance.submitted:
                raise ParseError("It is already submitted")
            if instance.done:
                raise ParseError("It is already done")
            answer = UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=instance, done=False).order_by(
                'created_at').last()
            if instance.theory_lab.type == 1:
                if 'github' not in validated_data:
                    raise ParseError("Send github link")
                answer.github = validated_data.pop('github')
            answer.end_time = timezone.now()
            answer.complete_time = (answer.end_time - answer.start_time).total_seconds()
            answer.done = True
            answer.save()
            ubm = get_object_or_404(UserBoughtCourseModel, user=instance.user,
                                    course=instance.theory_lab.theory.lesson.course)
            if ubm.trial:
                NotificationModel.objects.create(to_user=instance.user, type=8)
            else:
                NotificationModel.objects.create(to_user=instance.user, type=3)
                admins = ProfileModel.objects.filter(permission=3)
                for i in ubm.course.mentor.all():
                    admins = admins.exclude(user_id=i.user.id)
                    NotificationModel.objects.create(to_user=i.user, type=4, full_name=instance.user.get_full_name(),
                                                     lesson=instance.theory_lab.theory.lesson.title,
                                                     course=instance.theory_lab.theory.lesson.course.title_lms)
                for j in admins:
                    NotificationModel.objects.create(to_user=j.user, type=4, full_name=instance.user.get_full_name(),
                                                     lesson=instance.theory_lab.theory.lesson.title,
                                                     course=instance.theory_lab.theory.lesson.course.title_lms)
        return super(StudentTheoryLabSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        a = super(StudentTheoryLabSerializer, self).to_representation(instance)
        theory = instance.theory_lab.theory
        user = instance.user
        all1 = sorted(list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=theory, user=user)) + list(
            UserTheoryLabModel.objects.filter(theory_lab__theory=theory, user=user)), key=lambda x: x.created_at)
        if all1.index(instance) == len(all1) - 1:
            a['is_end'] = True
        else:
            a['is_end'] = False
        a['minimum_points'] = instance.theory_lab.minimum_points
        if TheoryLabChapterModel.objects.filter(
                theory__lesson__course=instance.theory_lab.theory.lesson.course).order_by(
            'created_at').first() == instance.theory_lab:
            a['first_lab'] = True
        else:
            a['first_lab'] = False
        if UserBoughtCourseModel.objects.get(user=user, course=theory.lesson.course).trial:
            if a['first_lab']:
                a['is_trial'] = True
            else:
                a['is_trial'] = False
        return a

    class Meta:
        model = UserTheoryLabModel
        fields = '__all__'
        read_only_fields = ['again', 'theory_lab', 'user', 'available', 'seen', 'done', 'again']


class CheckTheoryLabListSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        a = super(CheckTheoryLabListSerializer, self).to_representation(instance)
        a['course'] = instance.theory_lab.theory.lesson.course.title_lms
        a['lesson'] = instance.theory_lab.theory.lesson.title
        a['lab'] = instance.theory_lab.title
        a['full_name'] = f"{instance.user.first_name} {instance.user.last_name}"
        return a

    class Meta:
        model = UserTheoryLabModel
        fields = '__all__'


class CheckTheoryLabSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(min_value=0, write_only=True, max_value=100)
    comment = serializers.CharField(write_only=True, required=False)
    answered = serializers.SerializerMethodField()

    def get_answered(self, obj):
        if UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=obj).exists():
            return StudentTheoryLabAnsweredSerializer(
                UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=obj).order_by('created_at'), many=True).data
        else:
            return None

    def update(self, instance, validated_data):
        points = validated_data.pop('points')
        lab = instance.theory_lab
        if not instance.seen:
            raise ParseError("Student must see it")
        if 'comment' in validated_data:
            comment = validated_data.pop('comment')
        else:
            comment = None
        if lab.control:
            enough = True
        elif lab.minimum_points and points >= lab.minimum_points:
            enough = True
        else:
            enough = False
        answer = UserAnsweredTheoryLabModel.objects.filter(user_theory_lab=instance, user_theory_lab__submitted=True,
                                                           done=True).order_by(
            'created_at').last()
        answer.points = points
        answer.comment = comment
        answer.enough = enough
        answer.save()
        if lab.control or enough or (not lab.control and enough):
            instance.again = False
            if not instance.done and not instance.end_time:
                instance.end_time = timezone.now()
                instance.complete_time = (instance.end_time - instance.start_time).total_seconds()
            instance.done = True
            instance.save()
            theory = instance.theory_lab.theory
            all2 = sorted(
                list(UserTheoryChapterModel.objects.filter(theory_chapter__theory=theory, user=instance.user)) + list(
                    UserTheoryLabModel.objects.filter(theory_lab__theory=theory, user=instance.user)),
                key=lambda x: x.created_at)
            ind = all2.index(instance) + 1
            if index_in_list(all2, ind):
                all2[ind].available = True
                all2[ind].save()
            else:
                utm = get_object_or_404(UserTheoryModel, user=instance.user, theory=theory)
                if not utm.done:
                    utm.done = True
                if not utm.end_time:
                    utm.end_time = timezone.now()
                    utm.complete_time = (utm.end_time - utm.start_time).total_seconds()
                utm.save()
                lesson = theory.lesson
                all1 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=lesson, user=instance.user)) + list(
                    UserTestModel.objects.filter(test__lesson=lesson, user=instance.user)), key=lambda x: x.created_at)
                ind = all1.index(utm) + 1
                if index_in_list(all1, ind):
                    unlock_next(all1, ind, instance)
                else:
                    count_points(lesson=instance.theory_lab.theory.lesson, user=instance.user)
        elif not lab.control and not enough:
            instance.submitted = False
            instance.again = True
            instance.save()
        return super(CheckTheoryLabSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        a = super(CheckTheoryLabSerializer, self).to_representation(instance)
        a['course'] = instance.theory_lab.theory.lesson.course.title_lms
        a['lesson'] = instance.theory_lab.theory.lesson.title
        a['lab'] = instance.theory_lab.title
        a['full_name'] = f"{instance.user.first_name} {instance.user.last_name}"
        a['minimum_points'] = instance.theory_lab.minimum_points
        return a

    class Meta:
        model = UserTheoryLabModel
        fields = '__all__'
        read_only_fields = ['theory_lab', 'user', 'available', 'submitted', 'seen', 'done', 'again']


class StudentTestSerializer(serializers.ModelSerializer):
    test = TestCreateSerializer()

    def to_representation(self, instance):
        a = super(StudentTestSerializer, self).to_representation(instance)
        user = instance.user
        test = instance.test
        intros = UserTestIntroModel.objects.filter(user=user, test_intro__test=test)
        chapters = UserTestChapterModel.objects.filter(user=user, test_chapter__test=test)
        all1 = intros.count() + chapters.count()
        down = intros.filter(done=True).count() + chapters.filter(done=True).count()
        a["all"] = all1
        a["completed"] = down
        try:
            a["percentage"] = round(down * 100 / all1, 2)
        except ZeroDivisionError:
            a["percentage"] = 0
        return a

    class Meta:
        model = UserTestModel
        fields = '__all__'


class StudentTestDetailSerializer(serializers.ModelSerializer):
    test = TestCreateSerializer()
    intro = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()

    def get_intro(self, obj):
        if UserTestIntroModel.objects.filter(test_intro__in=TestIntroModel.objects.filter(test__usertestmodel=obj),
                                             user=self.context['request'].user).exists():
            data = StudentTestIntroSerializer(
                UserTestIntroModel.objects.get(test_intro=TestIntroModel.objects.get(test__usertestmodel=obj),
                                               user=self.context['request'].user), many=False,
                context=self.context).data
            if UserTestChapterModel.objects.filter(
                    test_chapter__in=TestChapterModel.objects.filter(test__usertestmodel=obj),
                    user=self.context['request'].user).exists():
                data['is_end'] = False
            else:
                data['is_end'] = True
            return data
        else:
            return None

    def get_chapters(self, obj):
        return UserTestChapterModel.objects.filter(
            test_chapter__in=TestChapterModel.objects.filter(test__usertestmodel=obj),
            user=self.context['request'].user).count()

    def to_representation(self, instance):
        a = super(StudentTestDetailSerializer, self).to_representation(instance)
        if instance.start:
            left = (instance.test_ending - timezone.now()).total_seconds()
            if left < 0:
                left = 0
            a['seconds_left'] = round(left)
        user = instance.user
        test = instance.test
        if UserBoughtCourseModel.objects.get(user=user, course=test.lesson.course).trial:
            utm = instance
            ulm = get_object_or_404(UserLessonModel, user=user, lesson=test.lesson)
            all1 = sorted(list(UserTheoryModel.objects.filter(user=user, theory__lesson=test.lesson)) + list(
                UserTestModel.objects.filter(user=user, test__lesson=test.lesson)), key=lambda x: x.created_at)
            if UserLessonModel.objects.filter(user=user, lesson__course=test.lesson.course).order_by(
                    'created_at').first() == ulm and all1.index(utm) == len(all1) - 1:
                a['is_trial'] = True
            else:
                a['is_trial'] = False
        return a

    class Meta:
        model = UserTestModel
        fields = '__all__'


class StudentTestIntroSerializer(serializers.ModelSerializer):
    test_intro = TestIntroCreateSerializer()

    def update(self, instance, validated_data):
        if "done" in validated_data and validated_data['done']:
            if not instance.seen:
                raise ParseError
            user = instance.user
            test = instance.test_intro.test
            next_th = UserTestChapterModel.objects.filter(test_chapter__test=test, user=user).order_by('created_at')
            if next_th.exists():
                pass
            else:
                utm = get_object_or_404(UserTestModel, user=user, test=test)
                if not utm.done:
                    utm.end_time = timezone.now()
                    utm.complete_time = (utm.end_time - utm.start_time).total_seconds()
                utm.done = True
                utm.save()
                lesson = test.lesson
                all1 = sorted(list(UserTheoryModel.objects.filter(theory__lesson=lesson, user=user)) + list(
                    UserTestModel.objects.filter(test__lesson=lesson, user=user)), key=lambda x: x.created_at)
                ind = all1.index(utm) + 1
                if index_in_list(all1, ind):
                    unlock_next(all1, ind, instance)
                else:
                    if not UserLessonOverallModel.objects.filter(
                            user_lesson=UserLessonModel.objects.get(lesson=lesson, user=user)).exists():
                        ulm = get_object_or_404(UserLessonModel, lesson=lesson, user=user)
                        if not ulm.done:
                            ulm.done = True
                        if not ulm.end_time:
                            ulm.end_time = timezone.now()
                            ulm.complete_time = (ulm.end_time - ulm.start_time).total_seconds()
                        ulm.save()
                        next_les = UserLessonModel.objects.filter(user=user, lesson=LessonModel.objects.filter(
                            pk__gt=lesson.pk, active=True, course=lesson.course).order_by('pk').first()).first()
                        if next_les:
                            if not next_les.done:
                                next_les.activation_date = ulm.end_time.date() + relativedelta(
                                    days=lesson.activation_day)
                                next_les.recommend_end_date = next_les.activation_date + relativedelta(
                                    days=lesson.recommend_end)
                                next_les.save()
                                lesson_activate_new(next_les)
                        else:
                            ubm = get_object_or_404(UserBoughtCourseModel, user=user, course=lesson.course)
                            ubm.end_time = timezone.now()
                            ubm.complete_time = (ubm.end_time - ubm.start_time).total_seconds()
                            ubm.completed = True
                            ubm.save()
        return super(StudentTestIntroSerializer, self).update(instance, validated_data)

    class Meta:
        model = UserTestIntroModel
        fields = '__all__'
        read_only_fields = ['test_intro', 'user', 'available', 'seen']


class TestStudentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestVariantModel
        exclude = ('answer', 'created_at', 'updated_at')


class TestChapterStudentSerializer(serializers.ModelSerializer):
    all_variants = serializers.SerializerMethodField('get_all')

    def get_all(self, obj):
        return TestStudentVariantSerializer(TestVariantModel.objects.filter(test_chapter=obj), many=True).data

    class Meta:
        model = TestChapterModel
        fields = '__all__'


class StudentTestChapterSerializer(serializers.ModelSerializer):
    test_chapter = TestChapterStudentSerializer()
    answered = serializers.JSONField(required=False, write_only=True)
    short_answer = serializers.CharField(required=False, write_only=True)

    def update(self, instance, validated_data):
        if 'answered' in validated_data or 'short_answer' in validated_data:
            hap = instance.test_chapter
            if UserAnsweredTestChapterModel.objects.filter(user_test=instance).order_by('created_at').last().done:
                raise ParseError("Question is already answered")
            answer_hap = UserAnsweredTestChapterModel.objects.filter(user_test=instance, done=False).order_by(
                'created_at').last()
            if 'answered' in validated_data:
                answer = validated_data.pop('answered')
                if hap.type == 0:
                    hap_sel = get_object_or_404(TestVariantModel, id=answer[0], test_chapter=hap)
                    answer_hap.correct = True if hap_sel.answer else False
                elif hap.type == 1:
                    all_tests = TestVariantModel.objects.filter(test_chapter=hap, answer=True)
                    ok = True
                    for a in answer:
                        if all_tests.filter(id=a).exists():
                            ok = True
                            all_tests = all_tests.exclude(id=a)
                        else:
                            ok = False
                    if all_tests.exists():
                        ok = False
                    answer_hap.correct = True if ok else False
                else:
                    raise ParseError("Wrong type")
            elif 'short_answer' in validated_data:
                answer = validated_data.pop('short_answer')
                answer_hap.correct = True if TestChapterModel.objects.filter(id=hap.id,
                                                                             short_answer__iexact=answer).exists() else False
            else:
                raise ParseError("Wrong answer type")
            answer_hap.end_time = timezone.now()
            answer_hap.complete_time = (answer_hap.end_time - answer_hap.start_time).total_seconds()
            answer_hap.done = True
            answer_hap.answered = answer
            answer_hap.save()
        else:
            raise ParseError("Send answer")
        if not instance.done and not instance.end_time:
            instance.end_time = timezone.now()
            instance.complete_time = (instance.end_time - instance.start_time).total_seconds()
        instance.done = True
        instance.save()
        last_inst = super(StudentTestChapterSerializer, self).update(instance, validated_data)
        next_test = UserTestChapterModel.objects.filter(pk__gt=instance.pk, test_chapter__test=hap.test,
                                                        user=instance.user).order_by('pk').first()
        if next_test:
            next_test.available = True
            next_test.save()
        else:
            utm = get_object_or_404(UserTestModel, test=instance.test_chapter.test, user=instance.user)
            end_test(request=self.context['request'], user_test=utm.id)
        return last_inst

    def to_representation(self, instance):
        a = super(StudentTestChapterSerializer, self).to_representation(instance)
        if instance == UserTestChapterModel.objects.filter(test_chapter__test=instance.test_chapter.test,
                                                           user=instance.user).order_by('created_at').last():
            a['is_end'] = True
        else:
            a['is_end'] = False
        test = get_object_or_404(UserTestModel, test=instance.test_chapter.test, user=instance.user)
        if test.start or test.done or test.again:
            answer_hap = UserAnsweredTestChapterModel.objects.filter(user_test=instance, done=True).order_by(
                'created_at').last()
            if answer_hap and answer_hap.done:
                if answer_hap.correct:
                    a['right'] = True
                else:
                    a['right'] = False
            left = (test.test_ending - timezone.now()).total_seconds()
            if left < 0:
                left = 0
            a['seconds_left'] = left
        return a

    class Meta:
        model = UserTestChapterModel
        exclude = ('created_at', 'updated_at')
        read_only_fields = ['test_chapter', 'user', 'available', 'seen', 'done']


class StudentTestPointsSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if not instance.done or not instance.user_test_model:
            return {"done": False}
        a = super(StudentTestPointsSerializer, self).to_representation(instance)
        test = instance.user_test_model.test
        a['lesson'] = get_object_or_404(UserLessonModel, user=instance.user_test_model.user, lesson=test.lesson).id
        if test.minimum_percentage:
            a['minimum_points'] = test.minimum_percentage
        else:
            a['minimum_points'] = None
        return a

    class Meta:
        model = UserAnsweredTestModel
        fields = '__all__'


class StudentOverallSerializer(serializers.ModelSerializer):
    points = serializers.IntegerField(source='usergotlessonoverallmodel.points')

    class Meta:
        model = UserLessonOverallModel
        fields = '__all__'
