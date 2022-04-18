import json
import os

import requests
import hashlib

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView, GenericAPIView, \
    UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import UserModel
from account.permissions import AdminPermission, StudentPermission, HighPermission, SAMPermission
from courses.models import CourseModel, FeedbackModel, SliderMainModel, UserBoughtCourseModel, LessonModel, \
    UserLessonModel, TheoryModel, TestModel, UserTheoryModel, TheoryIntroModel, UserTheoryIntroModel, UserTestModel, \
    TestIntroModel, UserTestIntroModel, UserTheoryChapterModel, UserTheoryLabModel, TeacherModel, EditorImageModel, \
    UserTestChapterModel, UserAnsweredTheoryLabModel, UserAnsweredTestModel, UserAnsweredTestChapterModel, \
    UserLessonOverallModel, TheoryChapterModel, TheoryLabChapterModel, TestChapterModel
from courses.serializers import CourseListSerializer, CourseDetailSerializer, RequestSerializer, FeedbackSerializer, \
    SliderSerializer, UserBoughtCourseCreateSerializer, UserBoughtCourseListSerializer, CourseCreateSerializer, \
    TheorySerializer, TestCreateSerializer, TheoryIntroCreateSerializer, \
    TheoryChapterCreateSerializer, TheoryLabCreateSerializer, TestChapterCreateSerializer, TestIntroCreateSerializer, \
    StudentLessonSerializer, StudentLessonDetailSerializer, LessonDetailSerializer, TheoryDetailSerializer, \
    TestDetailSerializer, StudentTheoryDetailSerializer, StudentTheoryIntroSerializer, StudentTheoryChapterSerializer, \
    StudentTheoryLabSerializer, StudentTestDetailSerializer, CheckTheoryLabSerializer, TeacherSerializer, \
    StudentTestIntroSerializer, LessonListSerializer, LessonCreateSerializer, EditorImageSerializer, \
    StudentTestChapterSerializer, end_test, count_points, StudentTestPointsSerializer, StudentOverallSerializer, \
    CheckTheoryLabListSerializer, UserTrialCourseCreateSerializer, lesson_activate_new, UserAssignCourseCreateSerializer
from courses.utils import index_in_list
from dashboard.models import NotificationModel, LogsModel, OrderModel


class EditorImageCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    queryset = EditorImageModel.objects.all()
    serializer_class = EditorImageSerializer


class EditorImageDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    queryset = EditorImageModel.objects.all()
    serializer_class = EditorImageSerializer
    lookup_url_kwarg = 'id'


class EditorParserView(APIView):

    def get(self, request):
        if not self.request.GET.get('url'):
            return Response("Send url", status=status.HTTP_200_OK)
        else:
            url = self.request.GET.get('url')
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            return Response("String is not valid URL", status=status.HTTP_404_NOT_FOUND)
        return Response(requests.get(f"https://codex.so/editor/fetchUrl?url={url}").json(), status=status.HTTP_200_OK)


class CourseListView(ListAPIView):
    queryset = CourseModel.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = [IsAuthenticated, AdminPermission]


class CourseAvailableListView(ListAPIView):
    queryset = CourseModel.objects.filter(active=True)
    serializer_class = CourseListSerializer
    permission_classes = [IsAuthenticated]


class CourseDetailView(RetrieveAPIView):
    """Send course`s slug in url kwargs"""
    serializer_class = CourseDetailSerializer

    def get_object(self):
        return get_object_or_404(CourseModel, id=self.kwargs['id'], active=True)

    def get(self, request, *args, **kwargs):
        return super(CourseDetailView, self).get(request)


class CourseAdminDetailView(RetrieveUpdateDestroyAPIView):
    """Send course`s slug in url kwargs"""
    serializer_class = CourseCreateSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def get_object(self):
        return get_object_or_404(CourseModel, id=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        return super(CourseAdminDetailView, self).get(request)


class RequestCreateView(CreateAPIView):
    serializer_class = RequestSerializer


class FeedbackListView(ListAPIView):
    queryset = FeedbackModel.objects.all()
    serializer_class = FeedbackSerializer


class TeacherListView(ListAPIView):
    queryset = TeacherModel.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, HighPermission]


class SliderListView(GenericAPIView):
    """Send course`s slug in url kwargs"""
    serializer_class = SliderSerializer

    def get_object(self):
        return get_object_or_404(SliderMainModel, course__slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)


class UserBoughtCourseCreateView(CreateAPIView):
    """Send course`s id, user`s id and status in POST body"""
    serializer_class = UserBoughtCourseCreateSerializer

    def get_serializer_context(self):
        context = super(UserBoughtCourseCreateView, self).get_serializer_context()
        merchant_trans_id = self.request.POST.get('merchant_trans_id')
        merchant_prepare_id = self.request.POST.get('merchant_prepare_id')
        order = get_object_or_404(OrderModel, id=merchant_trans_id, user_id=merchant_prepare_id)
        course_id = order.course.id
        if UserBoughtCourseModel.objects.filter(user_id=merchant_prepare_id, course_id=course_id, trial=True).exists():
            context.update({
                "trial": False,
            })
        click_trans_id = self.request.POST.get('click_trans_id')
        merchant_trans_id = self.request.POST.get('merchant_trans_id')
        merchant_prepare_id = self.request.POST.get('merchant_prepare_id')
        error_response = {
            "error": 0,
            "error_note": "Success",
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": merchant_prepare_id,
            "user_id": merchant_prepare_id,
            "course_id": course_id
        }
        context.update(error_response)
        return context

    def post(self, request, *args, **kwargs):
        if 'click_trans_id' not in request.POST or 'merchant_prepare_id' not in request.POST or 'error_note' not in request.POST or 'error' not in request.POST or 'click_paydoc_id' not in request.POST or 'service_id' not in request.POST or 'merchant_trans_id' not in request.POST or 'amount' not in request.POST or 'action' not in request.POST or 'sign_string' not in request.POST or 'sign_time' not in request.POST:
            error_response = {
                "error": -8,
                "error_note": "Error in request from click"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        click = os.getenv("CLICK")
        click_trans_id = request.POST.get('click_trans_id')
        service_id = request.POST.get('service_id')
        merchant_trans_id = request.POST.get('merchant_trans_id')
        amount = request.POST.get('amount')
        action = request.POST.get('action')
        error = request.POST.get('error')
        sign_time = request.POST.get('sign_time')
        merchant_prepare_id = request.POST.get('merchant_prepare_id')
        sign_string = request.POST.get('sign_string')
        if not OrderModel.objects.filter(id=merchant_trans_id).exists():
            error_response = {
                "error": -6,
                "error_note": "Transaction does not exist"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        else:
            order = get_object_or_404(OrderModel, id=merchant_trans_id)
        if order.status_payment == 2:
            error_response = {
                "error": -4,
                "error_note": "Already paid"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        course_id = order.course.id
        if not UserModel.objects.filter(id=merchant_prepare_id).exists() or not CourseModel.objects.filter(id=course_id,
                                                                                                           active=True).exists():
            error_response = {
                "error": -5,
                "error_note": "User does not exist"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        if not OrderModel.objects.filter(id=merchant_trans_id, user_id=merchant_prepare_id,
                                         course_id=course_id).exists():
            error_response = {
                "error": -6,
                "error_note": "Transaction does not exist"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(CourseModel, id=course_id)
        if int(action) != 1:
            error_response = {
                "error": -3,
                "error_note": "Action not found"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        if course.price != int(amount) or int(amount) != order.amount:
            error_response = {
                "error": -2,
                "error_note": "Incorrect parameter amount"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        result = hashlib.md5(
            f"{click_trans_id}{service_id}{click}{merchant_trans_id}{merchant_prepare_id}{amount}{1}{sign_time}".encode(
                "utf-8")).hexdigest()
        if result != sign_string:
            error_response = {
                "error": -1,
                "error_note": "SIGN CHECK FAILED!"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

        if order.status_payment == 4:
            error_response = {
                "error": -9,
                "error_note": "Transaction cancelled"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        error_response = {
            "error": 0,
            "error_note": "Success",
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": merchant_prepare_id,
        }
        LogsModel.objects.create(json=request.POST, url_type='complete', merchant_trans_id=merchant_trans_id)
        if int(error) < 0:
            OrderModel.objects.filter(id=merchant_trans_id, user_id=merchant_prepare_id, course_id=course_id).update(
                status_payment=4, click_trans_id=click_trans_id)
            error_response = {
                "error": -9,
                "error_note": "Transaction cancelled"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        OrderModel.objects.filter(id=merchant_trans_id, user_id=merchant_prepare_id, course_id=course_id).update(
            click_trans_id=click_trans_id, status_payment=2)
        if UserBoughtCourseModel.objects.filter(user_id=merchant_prepare_id, course_id=course_id, status=False,
                                                trial=False).exists():
            ub = get_object_or_404(UserBoughtCourseModel, user_id=merchant_prepare_id, course_id=course_id,
                                   status=False, trial=False)
            ub.status = True
            ub.expiration_date = timezone.now().date() + relativedelta(days=30)
            ub.save()
            NotificationModel.objects.create(to_user=ub.user, type=5, course=ub.course.title_lms)
            return Response(error_response, status=status.HTTP_200_OK)
        if UserBoughtCourseModel.objects.filter(user_id=merchant_prepare_id, course_id=course_id, status=True,
                                                trial=False).exists():
            ubm = get_object_or_404(UserBoughtCourseModel, user_id=merchant_prepare_id, course_id=course_id,
                                    status=True, trial=False)
            ubm.expiration_date = ubm.expiration_date + relativedelta(days=30)
            ubm.save()
            NotificationModel.objects.create(to_user=ubm.user, type=5, course=ubm.course.title_lms)
            return Response(error_response, status=status.HTTP_200_OK)
        return super(UserBoughtCourseCreateView, self).create(request)


class UserAssignCourseCreateView(CreateAPIView):
    """Send course`s id and user`s id POST body"""
    serializer_class = UserAssignCourseCreateSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def get_serializer_context(self):
        context = super(UserAssignCourseCreateView, self).get_serializer_context()
        body_unicode = self.request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user = body['user']
        course = body['course']
        if UserBoughtCourseModel.objects.filter(user_id=user, course_id=course, trial=True).exists():
            context.update({
                "trial": False
            })
        return context

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user = body['user']
        course = body['course']
        if CourseModel.objects.filter(id=course, active=False).exists():
            return Response("Course is not active", status=status.HTTP_406_NOT_ACCEPTABLE)
        if UserBoughtCourseModel.objects.filter(user_id=user, course_id=course, status=False, trial=False).exists():
            ub = get_object_or_404(UserBoughtCourseModel, user_id=user, course_id=course, status=False, trial=False)
            ub.status = True
            ub.expiration_date = timezone.now().date() + relativedelta(days=30)
            ub.save()
            NotificationModel.objects.create(to_user=ub.user, type=5, course=ub.course.title_lms)
            return Response("User renewed course", status=status.HTTP_406_NOT_ACCEPTABLE)
        if UserBoughtCourseModel.objects.filter(user_id=user, course_id=course, status=True, trial=False).exists():
            ubm = get_object_or_404(UserBoughtCourseModel, user_id=user, course_id=course, status=True, trial=False)
            ubm.expiration_date = ubm.expiration_date + relativedelta(days=30)
            ubm.save()
            NotificationModel.objects.create(to_user=ubm.user, type=9, course=ubm.course.title_lms)
            return Response("User extended course for 30 days", status=status.HTTP_208_ALREADY_REPORTED)
        return super(UserAssignCourseCreateView, self).create(request)


class UserUnassignedCourseDestroyView(DestroyAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = UserBoughtCourseCreateSerializer

    def get_object(self):
        return get_object_or_404(UserBoughtCourseModel, id=self.kwargs['id'])

    def destroy(self, request, *args, **kwargs):
        user = self.get_object().user
        UserLessonModel.objects.filter(user=user).delete()
        UserTheoryModel.objects.filter(user=user).delete()
        UserTheoryIntroModel.objects.filter(user=user).delete()
        UserTheoryChapterModel.objects.filter(user=user).delete()
        UserTheoryLabModel.objects.filter(user=user).delete()
        UserTestModel.objects.filter(user=user).delete()
        UserTestIntroModel.objects.filter(user=user).delete()
        UserTestChapterModel.objects.filter(user=user).delete()
        return super(UserUnassignedCourseDestroyView, self).destroy(request)


class UserTrialCourseCreateView(CreateAPIView):
    serializer_class = UserTrialCourseCreateSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user = request.user
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        course = body['course']
        if CourseModel.objects.filter(id=course, active=False).exists():
            return Response("Course is not active", status=status.HTTP_406_NOT_ACCEPTABLE)
        if UserBoughtCourseModel.objects.filter(user=user, course=course).exists():
            return Response("User already have this course", status=status.HTTP_406_NOT_ACCEPTABLE)
        if user.profile.used_trial or UserBoughtCourseModel.objects.filter(user=user, trial=True).exists():
            return Response("User already used trial", status=status.HTTP_406_NOT_ACCEPTABLE)
        return super(UserTrialCourseCreateView, self).create(request)


class UserBoughtCourseListView(ListAPIView):
    serializer_class = UserBoughtCourseListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserBoughtCourseModel.objects.filter(user=self.request.user, course__active=True)

    def list(self, request, *args, **kwargs):
        data = {
            'available': UserBoughtCourseModel.objects.filter(user=self.request.user).distinct().count(),
            'all': CourseModel.objects.filter(active=True).count(),
            'courses': UserBoughtCourseListSerializer(self.get_queryset(), many=True, context={'request': request}).data
        }
        return Response(data)


class CourseCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = CourseCreateSerializer

    def create(self, request, *args, **kwargs):
        if request.user.profile.permission != 3:
            return Response("Only admin can access", status=status.HTTP_403_FORBIDDEN)
        else:
            if CourseModel.objects.filter(title=request.POST.get('title'),
                                          slug=slugify(request.POST.get('title'))).exists():
                return Response("Title not unique", status=status.HTTP_409_CONFLICT)
            else:
                return super(CourseCreateView, self).create(request)


class LessonCreateView(CreateAPIView):
    """POST body: course id, title, preview, banner, activation_day"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = LessonCreateSerializer


class LessonListView(RetrieveAPIView):
    """GET params: course id"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = LessonListSerializer

    def get_object(self):
        return get_object_or_404(CourseModel, id=self.request.GET.get('course'))


class LessonDetailView(RetrieveAPIView):
    """Lesson id in url kwargs"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = LessonDetailSerializer
    queryset = LessonModel.objects.all()
    lookup_url_kwarg = 'id'


class LessonUpdateDeleteView(UpdateAPIView, DestroyAPIView):
    """Lesson id in url kwargs"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = LessonCreateSerializer

    def get_object(self):
        return get_object_or_404(LessonModel, id=self.kwargs['id'])

    def destroy(self, request, *args, **kwargs):
        lm = LessonModel.objects.filter(course=self.get_object().course, pk__gt=self.get_object().pk,
                                        active=True).order_by('pk')
        if lm.exists():
            b = lm.first()
            all1 = sorted(list(TheoryModel.objects.filter(lesson=b)) + list(TestModel.objects.filter(lesson=b)),
                          key=lambda x: x.created_at)
            for a in UserBoughtCourseModel.objects.filter(course=self.get_object().course).select_related('user'):
                ulm = get_object_or_404(UserLessonModel, lesson=self.get_object(), user=a.user)
                if ulm.available:
                    if UserLessonModel.objects.filter(lesson=b, user=a.user, available=False).exists():
                        UserLessonModel.objects.filter(lesson=b, user=a.user).update(available=True,
                                                                                     activation_date=ulm.activation_date)
                        if all1:
                            if all1[0].__class__.__name__ == "TheoryModel":
                                UserTheoryModel.objects.filter(theory=all1[0], user=a.user).update(available=True)
                                UserTheoryIntroModel.objects.filter(theory_intro__in=TheoryIntroModel.objects.filter(
                                    theory=all1[0]), user=a.user).update(available=True)
                            elif all1[0].__class__.__name__ == "TestModel":
                                UserTestModel.objects.filter(test=all1[0], user=a.user).update(available=True)
                                UserTestIntroModel.objects.filter(user=a.user,
                                                                  test_intro__in=TestIntroModel.objects.filter(
                                                                      test=all1[0])).update(available=True)
                else:
                    if ulm.activation_date:
                        UserLessonModel.objects.filter(lesson=b, user=a.user).update(
                            activation_date=ulm.activation_date)
        return super(LessonUpdateDeleteView, self).destroy(request)


class TheoryCreateView(CreateAPIView):
    """POST body: lesson id and title"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheorySerializer


class TheoryDetailView(RetrieveAPIView):
    """Theory id in url kwargs"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryDetailSerializer
    queryset = TheoryModel.objects.all()
    lookup_url_kwarg = 'id'


class TheoryUpdateDeleteView(UpdateAPIView, DestroyAPIView):
    """Theory id in url kwargs"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheorySerializer
    queryset = TheoryModel.objects.all()

    def get_object(self):
        return get_object_or_404(TheoryModel, id=self.kwargs['id'])

    # def delete(self, request, *args, **kwargs):
    #     theory = self.get_object()
    #     lesson = theory.lesson
    #     all1 = sorted(list(TheoryModel.objects.filter(lesson=lesson)) + list(TestModel.objects.filter(lesson=lesson)),
    #                   key=lambda x: x.created_at)
    #     lm = LessonModel.objects.filter(course=lesson.course, pk__gt=lesson.pk, active=True).order_by('pk')
    #     d = all1.index(theory) + 1
    #     for a in UserBoughtCourseModel.objects.filter(course=lesson.course).select_related('user'):
    #         ulm = get_object_or_404(UserLessonModel, lesson=lesson, user=a.user)
    #         utm = get_object_or_404(UserTheoryModel, theory=theory, user=a.user)
    #         if ulm.available:
    #             if utm.available:
    #
    #             else:
    #
    #         else:
    #             if lm.exists() and ulm.activation_date:
    #                 UserLessonModel.objects.filter(user=a.user, lesson=lm.first()).update(
    #                     activation_date=ulm.activation_date)
    #
    #     return super(TheoryUpdateDeleteView, self).delete(request)


class TheoryIntroCreateView(CreateAPIView):
    """POST body: theory id, title and text(editor js)"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryIntroCreateSerializer


class TheoryIntroDetailUpdateDeleteView(RetrieveAPIView, UpdateAPIView):
    """POST body: theory id, title and text(editor js)"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryIntroCreateSerializer

    def get_object(self):
        return get_object_or_404(TheoryIntroModel, id=self.kwargs['id'])

    # def delete(self, request, *args, **kwargs):
    #     return super(TheoryIntroDetailUpdateDeleteView, self).delete(request)


class TheoryChapterCreateView(CreateAPIView):
    """POST body: theory id, title, image and text(editor js)"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryChapterCreateSerializer


class TheoryChapterDetailUpdateDeleteView(RetrieveAPIView, UpdateAPIView):
    """POST body: theory id, title, image and text(editor js)"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryChapterCreateSerializer

    def get_object(self):
        return get_object_or_404(TheoryChapterModel, id=self.kwargs['id'])


class TheoryLabCreateView(CreateAPIView):
    """POST body: theory id, title, image and embed(replit lab url)"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryLabCreateSerializer


class TheoryLabDetailUpdateDeleteView(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TheoryLabCreateSerializer

    def get_object(self):
        return get_object_or_404(TheoryLabChapterModel, id=self.kwargs['id'])


class TestCreateView(CreateAPIView):
    """POST body: lesson id and title"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TestCreateSerializer


class TestDetailView(RetrieveAPIView, UpdateAPIView):
    """Test`s id in url kwargs"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TestDetailSerializer
    queryset = TestModel.objects.all()
    lookup_url_kwarg = 'id'


class TestIntroCreateView(CreateAPIView):
    """POST body: test id, image and text(editor js)"""
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TestIntroCreateSerializer


class TestIntroDetailUpdateDeleteView(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TestIntroCreateSerializer
    queryset = TestIntroModel.objects.all()
    lookup_url_kwarg = 'id'


class TestChapterCreateView(CreateAPIView):
    """POST body: test id, type(int), question(str), feedback_true(str), feedback_false(str) and short_answer(str,
    if type==2) """
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TestChapterCreateSerializer


class TestChapterDetailUpdateView(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = TestChapterCreateSerializer
    queryset = TestChapterModel.objects.all()
    lookup_url_kwarg = 'id'


class StudentLessonListView(ListAPIView):
    """GET params: course id"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentLessonSerializer

    def get_queryset(self):
        return UserLessonModel.objects.filter(lesson__course=self.request.GET.get('course'), user=self.request.user,
                                              lesson__active=True).order_by('created_at')

    def list(self, request, *args, **kwargs):
        if not self.request.GET.get('course'):
            return Response("Send course id", status.HTTP_406_NOT_ACCEPTABLE)
        if UserBoughtCourseModel.objects.filter(status=False, user=self.request.user,
                                                course__lesson__userlessonmodel__in=self.get_queryset()).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        return super(StudentLessonListView, self).list(request)


class StudentLessonDetailView(RetrieveAPIView):
    """Student`s lesson id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentLessonDetailSerializer
    queryset = UserLessonModel.objects.all()

    def get_object(self):
        return get_object_or_404(UserLessonModel, user=self.request.user, id=self.kwargs['id'], lesson__active=True,
                                 available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(status=False, user=self.request.user,
                                                course__lesson__userlessonmodel=self.get_object()).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if not a.start_time:
            a.start_time = timezone.now()
            a.save()
        return super(StudentLessonDetailView, self).get(request)


class StudentLessonPointsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentOverallSerializer

    def get_object(self):
        answer = UserLessonOverallModel.objects.filter(user_lesson=self.kwargs['id'], available=True,
                                                       user_lesson__user=self.request.user).order_by('created_at')
        if answer.exists():
            return answer.last()
        else:
            raise Http404()

    def get(self, request, *args, **kwargs):
        a = self.get_object()
        if not a.seen:
            a.seen = True
            a.save()
        return super(StudentLessonPointsView, self).get(request)


class StudentTheoryDetailView(RetrieveAPIView):
    """Student`s theory id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTheoryDetailSerializer

    def get_object(self):
        return get_object_or_404(UserTheoryModel, user=self.request.user, id=self.kwargs['id'],
                                 theory__lesson__active=True, available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(status=False, user=self.request.user,
                                                course__lesson__userlessonmodel__in=UserLessonModel.objects.filter(
                                                    lesson__theory__usertheorymodel=self.get_object())).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().theory.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().theory.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This theory is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if not a.seen:
            a.seen = True
        if not a.start_time:
            a.start_time = timezone.now()
        a.save()
        ulm = get_object_or_404(UserLessonModel, lesson=self.get_object().theory.lesson, user=a.user)
        if not ulm.start_time:
            ulm.start_time = timezone.now()
            ulm.save()
        return super(StudentTheoryDetailView, self).get(request)


class StudentTheoryIntroDetailView(RetrieveAPIView, UpdateAPIView):
    """Student`s theory intro id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTheoryIntroSerializer

    def get_object(self):
        return get_object_or_404(UserTheoryIntroModel, user=self.request.user, id=self.kwargs['id'], available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(course__lesson__in=LessonModel.objects.filter(
                theory__theoryintromodel__usertheoryintromodel=self.get_object()), status=False,
                user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().theory_intro.theory.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().theory_intro.theory.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This theory intro is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        ulm = get_object_or_404(UserLessonModel, lesson=a.theory_intro.theory.lesson, user=a.user)
        utm = get_object_or_404(UserTheoryModel, theory=a.theory_intro.theory, user=a.user)
        if not ulm.start_time:
            ulm.start_time = timezone.now()
            ulm.save()
        if not utm.seen:
            utm.seen = True
            utm.save()
        if not utm.start_time:
            utm.start_time = timezone.now()
            utm.save()
        if not a.seen:
            a.seen = True
            a.save()
        return super(StudentTheoryIntroDetailView, self).get(request)


class StudentTheoryChapterDetailView(RetrieveAPIView, UpdateAPIView):
    """Student`s theory chapter id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTheoryChapterSerializer

    def get_object(self):
        return get_object_or_404(UserTheoryChapterModel, user=self.request.user, id=self.kwargs['id'], available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(course__lesson__in=LessonModel.objects.filter(
                theory__theorychaptermodel__usertheorychaptermodel=self.get_object()), status=False,
                user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().theory_chapter.theory.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().theory_chapter.theory.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This theory chapter is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if not a.seen:
            a.seen = True
        if not a.start_time:
            a.start_time = timezone.now()
        a.save()
        return super(StudentTheoryChapterDetailView, self).get(request)


class StudentTheoryLabDetailView(RetrieveAPIView, UpdateAPIView):
    """Student`s theory lab id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTheoryLabSerializer

    def get_object(self):
        return get_object_or_404(UserTheoryLabModel, user=self.request.user, id=self.kwargs['id'], available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(course__lesson__in=LessonModel.objects.filter(
                theory__theorylabchaptermodel__usertheorylabmodel=self.get_object()), status=False,
                user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().theory_lab.theory.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().theory_lab.theory.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This theory lab is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if not a.seen:
            a.seen = True
        if not a.start_time:
            a.start_time = timezone.now()
        if (not a.submitted and not a.done or a.again) and not UserAnsweredTheoryLabModel.objects.filter(
                Q(user_theory_lab=a) & (
                        Q(done=False) | Q(user_theory_lab__done=True) | Q(user_theory_lab__submitted=True))).exists():
            UserAnsweredTheoryLabModel.objects.create(user_theory_lab=a, start_time=timezone.now())
        a.save()
        return super(StudentTheoryLabDetailView, self).get(request)


class CheckTheoryLabListView(ListAPIView):
    permission_classes = [IsAuthenticated, HighPermission]
    serializer_class = CheckTheoryLabListSerializer

    def get_queryset(self):
        q = UserTheoryLabModel.objects.filter(seen=True, submitted=True, done=False)
        for a in q:
            if UserBoughtCourseModel.objects.filter(user=a.user,
                                                    course=a.theory_lab.theory.lesson.course).exists() and UserBoughtCourseModel.objects.get(
                    user=a.user, course=a.theory_lab.theory.lesson.course).trial:
                q = q.exclude(id=a.id)
        if self.request.user.profile.permission == 2:
            tl = LessonModel.objects.filter(course__mentor=self.request.user.teachermodel)
            return q.filter(theory_lab__theory__lesson__in=tl)
        return q


class CheckTheoryLabView(RetrieveUpdateDestroyAPIView):
    """Student`s theory lab id in url kwargs"""
    permission_classes = [IsAuthenticated, HighPermission]
    serializer_class = CheckTheoryLabSerializer

    def get_object(self):
        obj = get_object_or_404(UserTheoryLabModel, seen=True, submitted=True, done=False, id=self.kwargs['id'])
        get_object_or_404(UserBoughtCourseModel, user=obj.user, course=obj.theory_lab.theory.lesson.course, trial=False)
        return obj


class StudentTestDetailView(RetrieveAPIView):
    """Student`s test id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTestDetailSerializer

    def get_object(self):
        return get_object_or_404(UserTestModel, user=self.request.user, id=self.kwargs['id'], test__lesson__active=True,
                                 available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(status=False, user=self.request.user,
                                                course__lesson__userlessonmodel__in=UserLessonModel.objects.filter(
                                                    lesson__test__usertestmodel=self.get_object())).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().test.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().test.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This test is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if not a.seen:
            a.seen = True
            a.save()
        ulm = get_object_or_404(UserLessonModel, lesson=self.get_object().test.lesson, user=self.request.user)
        if not ulm.start_time:
            ulm.start_time = timezone.now()
            ulm.save()
        return super(StudentTestDetailView, self).get(request)


class StudentTestIntroDetailView(RetrieveAPIView, UpdateAPIView):
    """Student`s test intro id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTestIntroSerializer

    def get_object(self):
        return get_object_or_404(UserTestIntroModel, user=self.request.user, id=self.kwargs['id'], available=True)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(course__lesson__in=LessonModel.objects.filter(
                test__testintromodel__usertestintromodel=self.get_object()), status=False,
                user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().test_intro.test.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().test_intro.test.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This test intro is not available", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        ulm = get_object_or_404(UserLessonModel, lesson=a.test_intro.test.lesson, user=a.user)
        utm = get_object_or_404(UserTestModel, test=a.test_intro.test, user=a.user)
        if not ulm.start_time:
            ulm.start_time = timezone.now()
            ulm.save()
        if not utm.seen:
            utm.seen = True
            utm.save()
        if not utm.start_time:
            utm.start_time = timezone.now()
            utm.save()
        if not a.seen:
            a.seen = True
            a.save()
        return super(StudentTestIntroDetailView, self).get(request)


class StudentTestCurrentChapterView(RetrieveAPIView):
    """Student`s test current chapter; test id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTestChapterSerializer

    def get_object(self):
        test = UserTestChapterModel.objects.filter(test_chapter__test__usertestmodel=self.kwargs['id'],
                                                   user=self.request.user, done=False, available=True).order_by(
            'created_at')
        if test.exists():
            return test.first()
        else:
            raise Http404()

    def get(self, request, *args, **kwargs):
        test = get_object_or_404(UserTestModel, id=self.kwargs['id'], user=self.request.user, seen=True, done=False,
                                 available=True)
        if not test.available:
            return Response("This test is not available", status=status.HTTP_403_FORBIDDEN)
        if not test.seen:
            return Response("This test is not seen", status.HTTP_403_FORBIDDEN)
        if test.done:
            return Response("This test is done", status.HTTP_403_FORBIDDEN)
        if UserBoughtCourseModel.objects.filter(course__lesson__in=LessonModel.objects.filter(
                test__usertestmodel=test), status=False, user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not test.test.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user, lesson=test.test.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if self.request.query_params.get('start'):
            start = True if self.request.query_params.get('start').lower() == 'true' else False
        else:
            start = None
        if start is not None and start and not test.start:
            test.start = True
            test.trying += 1
            if not test.start_time:
                test.start_time = timezone.now()
            if not test.test_ending or test.again:
                test.test_ending = timezone.now() + relativedelta(seconds=test.test.timer)
            if test.start and (not test.done or test.again) and not UserAnsweredTestModel.objects.filter(
                    Q(user_test_model=test) & (Q(done=False) | Q(user_test_model__done=True))):
                UserAnsweredTestModel.objects.create(user_test_model=test, start_time=timezone.now())
            test.save()
            intro = get_object_or_404(UserTestIntroModel, user=self.request.user, test_intro__test=test.test)
            if not intro.seen:
                intro.seen = True
            if not intro.done:
                intro.done = True
            intro.save()
            next_th = UserTestChapterModel.objects.filter(test_chapter__test=test.test,
                                                          user=self.request.user).order_by(
                'created_at')
            if next_th.exists() and not next_th.first().available:
                next_test = next_th.first()
                next_test.available = True
                next_test.save()
        if not test.start:
            return Response("This test is not started", status=status.HTTP_403_FORBIDDEN)
        if UserTestIntroModel.objects.filter(seen=False, user=self.request.user, test_intro__test=test.test):
            return Response("This test intro is not seen", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if not a.available:
            return Response("This test chapter is not available", status.HTTP_403_FORBIDDEN)
        if not a.seen:
            a.seen = True
        if not a.start_time:
            a.start_time = timezone.now()
        a.save()
        if not UserAnsweredTestChapterModel.objects.filter(
                Q(user_test=a) & (Q(done=False) | Q(user_test__done=True))) and UserAnsweredTestModel.objects.filter(
            user_test_model=test, done=False) and test.start and (not test.done or test.again) and not a.done:
            UserAnsweredTestChapterModel.objects.create(user_test=a, start_time=timezone.now())
        return super(StudentTestCurrentChapterView, self).get(request)


class StudentTestChapterDetailView(UpdateAPIView):
    """Student`s test chapter id in url kwargs"""
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTestChapterSerializer

    def get_object(self):
        return get_object_or_404(UserTestChapterModel, id=self.kwargs['id'], user=self.request.user, seen=True,
                                 available=True)

    def patch(self, request, *args, **kwargs):
        a = self.get_object()
        test = get_object_or_404(UserTestModel, test=a.test_chapter.test, user=self.request.user)
        if not test.seen:
            return Response("This test is not seen", status.HTTP_403_FORBIDDEN)
        if UserTestIntroModel.objects.filter(seen=False, user=self.request.user, test_intro__test=test.test):
            return Response("This test intro is not seen", status.HTTP_403_FORBIDDEN)
        if UserBoughtCourseModel.objects.filter(course__lesson__in=LessonModel.objects.filter(
                test__testchaptermodel__usertestchaptermodel=self.get_object()), status=False,
                user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not a.test_chapter.test.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().test_chapter.test.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not a.available:
            return Response("This test chapter is not available", status.HTTP_403_FORBIDDEN)
        if not test.available:
            return Response("This test is not available", status=status.HTTP_403_FORBIDDEN)
        if not test.start:
            return Response("This test is not started", status=status.HTTP_403_FORBIDDEN)
        if test.done:
            return Response("This test is done", status.HTTP_403_FORBIDDEN)
        return super(StudentTestChapterDetailView, self).patch(request)


class StudentTestEndView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTestDetailSerializer

    def get_object(self):
        return get_object_or_404(UserTestModel, id=self.kwargs['id'], user=self.request.user, start=True,
                                 available=True, seen=True, done=False)

    def get(self, request, *args, **kwargs):
        if UserBoughtCourseModel.objects.filter(
                course__lesson__in=LessonModel.objects.filter(test__usertestmodel=self.get_object()), status=False,
                user=self.request.user).exists():
            return Response("You did not paid for this course", status.HTTP_403_FORBIDDEN)
        if not self.get_object().test.lesson.active:
            return Response("This lesson is not active", status.HTTP_403_FORBIDDEN)
        if UserLessonModel.objects.filter(available=False, user=self.request.user,
                                          lesson=self.get_object().test.lesson).exists():
            return Response("This lesson is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().available:
            return Response("This test is not available", status.HTTP_403_FORBIDDEN)
        if not self.get_object().seen:
            return Response("This test is not seen", status.HTTP_403_FORBIDDEN)
        a = self.get_object()
        if UserTestIntroModel.objects.filter(seen=False, user=self.request.user, test_intro__test=a.test):
            return Response("This test intro is not seen", status.HTTP_403_FORBIDDEN)
        if a.done:
            return Response("This test is done", status.HTTP_403_FORBIDDEN)
        step = super(StudentTestEndView, self).get(request)
        end_test(request, user_test=self.get_object().id)
        return step


class StudentTestPointsDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, SAMPermission]
    serializer_class = StudentTestPointsSerializer

    def get_object(self):
        answer = UserAnsweredTestModel.objects.filter(user_test_model=self.kwargs['id'], done=True,
                                                      user_test_model__user=self.request.user).order_by('created_at')
        if answer.exists():
            return answer.last()
        else:
            raise Http404()
