import base64
import hashlib
import json
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import renderer_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView, \
    RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import UserModel, ProfileModel
from account.permissions import AdminPermission
from courses.models import CourseModel, UserBoughtCourseModel, UserLessonModel, UserTheoryModel, UserTestModel, \
    UserTheoryLabModel, LessonModel, TheoryModel, TestModel, TestChapterModel
from courses.serializers import lesson_activate_new
from courses.utils import rep_att
from dashboard.models import KnowledgeBaseModel, NotificationModel, LogsModel, OrderModel, PaymeModel
from dashboard.serializers import KnowledgeBaseCreateListSerializer, KnowledgeBaseDetailSerializer, \
    StatisticsSerializer, StatCourseSerializer, KnowledgeVideoSerializer, KnowledgeBookSerializer, \
    NotificationListSerializer, HelpListSerializer, ProfileDashboardSerializer, OrderSerializer, PrepareSerializer, \
    OrderPaymeSerializer, StatisticsCoursesSerializer, StatisticsLessonsSerializer, StatisticsTheoryTestSerializer, \
    StatisticsTheoryDetailSerializer, StatisticsTestDetailSerializer, StatisticsUsersSerializer, \
    StatUserDetailSerializer, StatisticsUserCourseSerializer, StatisticsUserLessonSerializer, \
    StatisticsUserTheorySerializer, StatisticsUserTestSerializer


class OrderCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer


class OrderPaymeView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderPaymeSerializer


class KnowledgeBaseCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = KnowledgeBaseCreateListSerializer


class KnowledgeVideoCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = KnowledgeVideoSerializer


class KnowledgeBookCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = KnowledgeBookSerializer


class KnowledgeBaseListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = KnowledgeBaseCreateListSerializer
    queryset = KnowledgeBaseModel.objects.all()


class KnowledgeBaseDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = KnowledgeBaseDetailSerializer
    queryset = KnowledgeBaseModel.objects.all()
    lookup_url_kwarg = 'id'


class ProfileDashboardView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileDashboardSerializer

    def get_object(self):
        return get_object_or_404(ProfileModel, user=self.request.user)


class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = UserModel.objects.filter(profile__permission=1, userboughtcoursemodel__trial=False)
        if 'course' in self.request.query_params:
            users = UserModel.objects.filter(profile__permission=1, userboughtcoursemodel__course__trial=False,
                                             userboughtcoursemodel__course=self.request.query_params.get('course'))
            if 'lesson' in self.request.query_params:
                users = users.filter(userlessonmodel__lesson=self.request.query_params.get('lesson'),
                                     userlessonmodel__done=True)
        data = StatisticsSerializer(users, many=True, context={"request": self.request}).data
        data = sorted(data, key=lambda x: (x['gpa'], x['points']), reverse=True)
        i = 1
        for a in data:
            a['position'] = i
            i += 1
        return Response(data=data, status=status.HTTP_200_OK)


class StatisticsMenuView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StatCourseSerializer
    queryset = CourseModel.objects.filter(active=True)


class NotificationListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationListSerializer

    def get_queryset(self):
        NotificationModel.objects.filter(to_user=self.request.user).update(seen=True)
        return NotificationModel.objects.filter(to_user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        return super(NotificationListView, self).list(request)


class HelpListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HelpListSerializer

    def get_queryset(self):
        return UserBoughtCourseModel.objects.filter(user=self.request.user)


class PrepareView(GenericAPIView):
    serializer_class = PrepareSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        click = os.getenv("CLICK")
        if 'click_trans_id' not in data or 'error_note' not in data or 'error' not in data or 'click_paydoc_id' not in data or 'service_id' not in data or 'amount' not in data or 'action' not in data or 'merchant_trans_id' not in data or 'sign_string' not in data or 'sign_time' not in data:
            error_response = {
                "error": -8,
                "error_note": "Error in request from click"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        click_trans_id = data['click_trans_id']
        service_id = data['service_id']
        merchant_trans_id = data['merchant_trans_id']
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
        user_id = order.user.id
        course_id = order.course.id
        if not UserModel.objects.filter(id=user_id).exists() or not CourseModel.objects.filter(id=course_id,
                                                                                               active=True).exists():
            error_response = {
                "error": -5,
                "error_note": "User does not exist"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        amount = data['amount']
        action = data['action']
        error = data['error']
        sign_time = data['sign_time']
        sign_string = data['sign_string']
        result = hashlib.md5(
            f"{click_trans_id}{service_id}{click}{merchant_trans_id}{amount}{0}{sign_time}".encode(
                "utf-8")).hexdigest()
        course = get_object_or_404(CourseModel, id=course_id)
        if int(action) != 0:
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
            "merchant_prepare_id": order.user.id,
        }
        LogsModel.objects.create(json=data, url_type='prepare', merchant_trans_id=data['merchant_trans_id'])
        if int(error) < 0:
            OrderModel.objects.filter(id=merchant_trans_id, user_id=user_id, course_id=course_id).update(
                status_payment=4, click_trans_id=click_trans_id)
            error_response = {
                "error": -9,
                "error_note": "Transaction cancelled"
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        OrderModel.objects.filter(id=merchant_trans_id, user_id=user_id, course_id=course_id).update(
            click_trans_id=click_trans_id, status_payment=1)
        return Response(error_response, status=status.HTTP_200_OK)


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def paymeview(request):
    if request.method == 'POST':
        message = os.getenv('PAYME_TEST')
        message2 = os.getenv('PAYME')
        base64_string = base64.b64encode(message.encode('ascii')).decode("ascii")
        base64_string2 = base64.b64encode(message2.encode('ascii')).decode("ascii")
        nonauth = f"Basic {base64_string}"
        nonauth2 = f"Basic {base64_string2}"
        if 'HTTP_AUTHORIZATION' not in request.META or (
                request.META['HTTP_AUTHORIZATION'] != nonauth and request.META['HTTP_AUTHORIZATION'] != nonauth2):
            error_response = {
                "error": {
                    "code": -32504,
                    "message": "Недостаточно привилегий для выполнения метода.",
                },
            }
            return JsonResponse(error_response)
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        if 'method' not in body:
            error_response = {
                "error": {
                    "code": -32600,
                    "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                }
            }
            return JsonResponse(error_response)
        method = body['method']
        if method != 'CheckPerformTransaction' and method != 'GetStatement' and method != 'PerformTransaction' and method != 'CreateTransaction' and method != 'CancelTransaction' and method != 'CheckTransaction':
            error_response = {
                "error": -32601,
                "error_note": "Запрашиваемый метод не найден."
            }
            return JsonResponse(error_response)
        if method == 'CheckPerformTransaction':
            if 'params' not in body:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            params = body['params']
            if 'amount' not in params or 'account' not in params:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации. 3",
                    }
                }
                return JsonResponse(error_response)
            account = params['account']
            if 'phone' not in account or 'course_id' not in account or 'order_id' not in account:
                error_response = {
                    "error": {
                        "code": -31050,
                        "message": {"ru": "В account отсутствуют поля phone/course_id/order_id.",
                                    "en": "No fields phone/course_id/order_id.",
                                    "uz": "phone/course_id/order_id yoq"},
                    }
                }
                return JsonResponse(error_response)
            phone = account['phone'].replace("+", "").replace("-", "").replace(" ", "")
            if not UserModel.objects.filter(profile__phone=phone).exists():
                error_response = {
                    "error": {
                        "code": -31060,
                        "message": {"ru": "Отсутствует пользователь с таким номером.",
                                    "en": "No user with this phone.",
                                    "uz": "Bu user telefonni yoq"},
                    }
                }
                return JsonResponse(error_response)
            course_id = account['course_id']
            if not CourseModel.objects.filter(id=course_id).exists() or CourseModel.objects.filter(id=course_id,
                                                                                                   active=False).exists():
                error_response = {
                    "error": {
                        "code": -31070,
                        "message": {"ru": "Отсутствует курс.",
                                    "en": "No course.",
                                    "uz": "Bu kursni yoq"},
                    }
                }
                return JsonResponse(error_response)
            order_id = account['order_id']
            amount = int(int(params['amount']) / 100)
            if not PaymeModel.objects.filter(id=order_id, user__profile__phone=phone, course_id=course_id).exists():
                error_response = {
                    "error": {
                        "code": -31075,
                        "message": "Транзакция не найдена.",
                    },
                }
                return JsonResponse(error_response)
            payme = get_object_or_404(PaymeModel, id=order_id, user__profile__phone=phone, course_id=course_id)
            if amount != payme.course.price:
                error_response = {
                    "error": {
                        "code": -31001,
                        "message": f"Неверная сумма. {amount}",
                    },
                }
                return JsonResponse(error_response)
            if payme.status_payment == 1:
                error_response = {
                    "error": {
                        "code": -31088,
                        "message": "Обрабаытвается",
                    },
                }
                return JsonResponse(error_response)
            elif payme.status_payment == 2:
                error_response = {
                    "error": {
                        "code": -31088,
                        "message": "счет уже оплачен",
                    },
                }
                return JsonResponse(error_response)
            elif payme.status_payment == -1:
                error_response = {
                    "error": {
                        "code": -31087,
                        "message": "счет отменен",
                    },
                }
                return JsonResponse(error_response)
            error_response = {
                "result": {
                    "allow": True
                },
            }
            return JsonResponse(error_response)
        elif method == "CreateTransaction":
            if 'params' not in body:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            params = body['params']
            if 'amount' not in params or 'account' not in params or 'id' not in params or 'time' not in params:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            id = params['id']
            time = int(params['time'])
            account = params['account']
            if 'phone' not in account or 'course_id' not in account or 'order_id' not in account:
                error_response = {
                    "error": {
                        "code": -31050,
                        "message": {"ru": "В account отсутствуют поля phone/course_id/order_id.",
                                    "en": "No fields phone/course_id/order_id.",
                                    "uz": "phone/course_id/order_id yoq"},
                    }
                }
                return JsonResponse(error_response)
            phone = account['phone'].replace("+", "").replace("-", "").replace(" ", "")
            if not UserModel.objects.filter(profile__phone=phone).exists():
                error_response = {
                    "error": {
                        "code": -31060,
                        "message": {"ru": "Отсутствует пользователь с таким номером.",
                                    "en": "No user with this phone.",
                                    "uz": "Bu user telefonni yoq"},
                    }
                }
                return JsonResponse(error_response)
            course_id = account['course_id']
            if not CourseModel.objects.filter(id=course_id).exists() or CourseModel.objects.filter(id=course_id,
                                                                                                   active=False).exists():
                error_response = {
                    "error": {
                        "code": -31070,
                        "message": {"ru": "Отсутствует курс.",
                                    "en": "No course.",
                                    "uz": "Bu kursni yoq"},
                    }
                }
                return JsonResponse(error_response)
            order_id = account['order_id']
            amount = int(int(params['amount']) / 100)
            if not PaymeModel.objects.filter(paycom_transaction_id=id).exists():
                if not PaymeModel.objects.filter(id=order_id, user__profile__phone=phone, course_id=course_id).exists():
                    error_response = {
                        "error": {
                            "code": -31075,
                            "message": "Транзакция не найдена.",
                        },
                    }
                    return JsonResponse(error_response)
                payme = get_object_or_404(PaymeModel, id=order_id, user__profile__phone=phone, course_id=course_id)
                if amount != payme.course.price:
                    error_response = {
                        "error": {
                            "code": -31001,
                            "message": f"Неверная сумма 2. {amount}",
                        },
                    }
                    return JsonResponse(error_response)
                if payme.paycom_transaction_id is not None and payme.paycom_transaction_id != id:
                    error_response = {
                        "error": {
                            "code": -31080,
                            "message": "Вызов метода CreateTransaction с новой транзакцией.",
                        },
                    }
                    return JsonResponse(error_response)
                payme.paycom_transaction_id = id
                payme.create_time = timezone.now()
                payme.status_payment = 1
                timestmp = datetime.timestamp(payme.create_time) * 1000
                payme.save()
                error_response = {
                    "result": {
                        "create_time": timestmp,
                        "transaction": f"{payme.id}",
                        "state": 1
                    },
                }
                return JsonResponse(error_response)
            else:
                payme = get_object_or_404(PaymeModel, paycom_transaction_id=id)
                if amount != payme.course.price:
                    error_response = {
                        "error": {
                            "code": -31001,
                            "message": f"Неверная сумма 3. {amount}",
                        },
                    }
                    return JsonResponse(error_response)
                if payme.status_payment == 1:
                    addtime = payme.create_time + relativedelta(seconds=43200)
                    if timezone.now() > addtime:
                        payme.status_payment = -1
                        payme.reason = 4
                        payme.save()
                        error_response = {
                            "error": {
                                "code": -31008,
                                "message": "Невозможно выполнить операцию.",
                            },
                        }
                        return JsonResponse(error_response)
                    else:
                        timestmp = datetime.timestamp(payme.create_time) * 1000
                        error_response = {
                            "result": {
                                "create_time": timestmp,
                                "transaction": f"{payme.id}",
                                "state": 1
                            },
                        }
                        return JsonResponse(error_response)
                else:
                    error_response = {
                        "error": {
                            "code": -31008,
                            "message": "Невозможно выполнить операцию.",
                        },
                    }
                    return JsonResponse(error_response)
        elif method == 'CheckTransaction':
            if 'params' not in body:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            params = body['params']
            if 'id' not in params:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            id = params['id']
            if not PaymeModel.objects.filter(paycom_transaction_id=id).exists():
                error_response = {
                    "error": {
                        "code": -31003,
                        "message": "Транзакция не найдена.",
                    }
                }
                return JsonResponse(error_response)
            payme = get_object_or_404(PaymeModel, paycom_transaction_id=id)
            if payme.create_time is None:
                create_time = 0
            else:
                create_time = datetime.timestamp(payme.create_time) * 1000
            if payme.perform_time is None:
                perform_time = 0
            else:
                perform_time = datetime.timestamp(payme.perform_time) * 1000
            if payme.cancel_time is None:
                cancel_time = 0
            else:
                cancel_time = datetime.timestamp(payme.cancel_time) * 1000
            error_response = {
                "result": {
                    "create_time": create_time,
                    "transaction": f"{payme.id}",
                    "state": payme.status_payment,
                    "perform_time": perform_time,
                    "cancel_time": cancel_time,
                    "reason": payme.reason
                }
            }
            return JsonResponse(error_response)
        elif method == 'PerformTransaction':
            if 'params' not in body:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            params = body['params']
            if 'id' not in params:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            id = params['id']
            if not PaymeModel.objects.filter(paycom_transaction_id=id).exists():
                error_response = {
                    "error": {
                        "code": -31003,
                        "message": "Транзакция не найдена.",
                    }
                }
                return JsonResponse(error_response)
            payme = get_object_or_404(PaymeModel, paycom_transaction_id=id)
            if payme.status_payment == 1:
                addtime = payme.create_time + relativedelta(seconds=43200)
                if timezone.now() > addtime:
                    payme.status_payment = -1
                    payme.reason = 4
                    payme.save()
                    error_response = {
                        "error": {
                            "code": -31008,
                            "message": "Невозможно выполнить операцию.",
                        },
                    }
                    return JsonResponse(error_response)
                if UserBoughtCourseModel.objects.filter(user=payme.user, course=payme.course, status=False,
                                                        trial=False).exists():
                    ub = get_object_or_404(UserBoughtCourseModel, user=payme.user, course=payme.course, status=False,
                                           trial=False)
                    ub.status = True
                    ub.expiration_date = timezone.now().date() + relativedelta(days=30)
                    ub.save()
                    NotificationModel.objects.create(to_user=ub.user, type=5, course=ub.course.title_lms)
                    payme.status_payment = 2
                    payme.perform_time = timezone.now()
                    perform_time = datetime.timestamp(payme.perform_time) * 1000
                    payme.save()
                    error_response = {
                        "result": {
                            "transaction": f"{payme.id}",
                            "perform_time": perform_time,
                            "state": 2
                        }
                    }
                    return JsonResponse(error_response)
                if UserBoughtCourseModel.objects.filter(user=payme.user, course=payme.course, status=True,
                                                        trial=False).exists():
                    ubm = get_object_or_404(UserBoughtCourseModel, user=payme.user, course=payme.course, status=True,
                                            trial=False)
                    ubm.expiration_date = ubm.expiration_date + relativedelta(days=30)
                    ubm.save()
                    NotificationModel.objects.create(to_user=ubm.user, type=5, course=ubm.course.title_lms)
                    payme.status_payment = 2
                    payme.perform_time = timezone.now()
                    perform_time = datetime.timestamp(payme.perform_time) * 1000
                    payme.save()
                    error_response = {
                        "result": {
                            "transaction": f"{payme.id}",
                            "perform_time": perform_time,
                            "state": 2
                        }
                    }
                    return JsonResponse(error_response)
                if ProfileModel.objects.get(user=payme.user).permission == 0:
                    ProfileModel.objects.filter(user=payme.user).update(permission=1)
                if UserBoughtCourseModel.objects.filter(user=payme.user, course=payme.course, trial=True).exists():
                    ubm = get_object_or_404(UserBoughtCourseModel, user=payme.user, course=payme.course, trial=True)
                    ubm.trial = False
                    ubm.status = True
                    ubm.expiration_date = timezone.now().date() + relativedelta(days=30)
                    ubm.save()
                    if UserLessonModel.objects.filter(user=payme.user, lesson__course=payme.course, lesson__active=True,
                                                      available=True).exists():
                        fl = UserLessonModel.objects.filter(user=payme.user, lesson__course=payme.course,
                                                            lesson__active=True, available=True).select_related(
                            'lesson').order_by('created_at').first()
                        tla = sorted(list(
                            UserTestModel.objects.filter(user=payme.user, test__lesson=fl.lesson, done=True)) + list(
                            UserTheoryLabModel.objects.filter(user=payme.user, theory_lab__theory__lesson=fl.lesson)),
                                     key=lambda x: x.created_at)
                        if tla and tla[-1].done:
                            next_les = UserLessonModel.objects.filter(user=payme.user,
                                                                      lesson=LessonModel.objects.filter(
                                                                          course=payme.course, pk__gt=fl.lesson.pk,
                                                                          active=True).order_by('pk').first()).first()
                            if next_les:
                                if next_les.activation_date is None:
                                    next_les.activation_date = fl.end_time.date() + relativedelta(
                                        days=fl.lesson.activation_day)
                                if next_les.recommend_end_date is None:
                                    next_les.recommend_end_date = next_les.activation_date + relativedelta(
                                        days=fl.lesson.recommend_end)
                                next_les.save()
                                lesson_activate_new(next_les)
                        else:
                            if UserTheoryLabModel.objects.filter(theory_lab__theory__lesson=fl.lesson, user=payme.user,
                                                                 submitted=True).exists():
                                NotificationModel.objects.create(to_user=payme.user, type=3)
                                for po in fl.lesson.course.mentor.all():
                                    NotificationModel.objects.create(to_user=po.user, type=4,
                                                                     full_name=payme.user.get_full_name(),
                                                                     lesson=fl.lesson.title,
                                                                     course=payme.course.title_lms)
                    NotificationModel.objects.create(to_user=payme.user, type=5, course=payme.course.title_lms)
                    payme.status_payment = 2
                    payme.perform_time = timezone.now()
                    perform_time = datetime.timestamp(payme.perform_time) * 1000
                    payme.save()
                    error_response = {
                        "result": {
                            "transaction": f"{payme.id}",
                            "perform_time": perform_time,
                            "state": 2
                        }
                    }
                    return JsonResponse(error_response)
                else:
                    ubm = UserBoughtCourseModel.objects.create(course=payme.course, user=payme.user, status=True,
                                                               trial=False, bought_date=timezone.now().date(),
                                                               start_time=timezone.now(),
                                                               expiration_date=timezone.now().date() + relativedelta(
                                                                   days=30))
                rep_att(ubm, payme.course, payme.user)
                NotificationModel.objects.create(to_user=payme.user, type=5, course=payme.course.title_lms)
                payme.status_payment = 2
                payme.perform_time = timezone.now()
                perform_time = datetime.timestamp(payme.perform_time) * 1000
                payme.save()
                error_response = {
                    "result": {
                        "transaction": f"{payme.id}",
                        "perform_time": perform_time,
                        "state": 2
                    }
                }
                return JsonResponse(error_response)
            else:
                if payme.status_payment == 2:
                    perform_time = datetime.timestamp(payme.perform_time) * 1000
                    error_response = {
                        "result": {
                            "transaction": f"{payme.id}",
                            "perform_time": perform_time,
                            "state": 2
                        }
                    }
                    return JsonResponse(error_response)
                else:
                    error_response = {
                        "error": {
                            "code": -31008,
                            "message": "Невозможно выполнить операцию. Ошибка возникает если состояние транзакции, не позволяет выполнить операцию.",
                        },
                    }
                    return JsonResponse(error_response)
        elif method == 'CancelTransaction':
            if 'params' not in body:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            params = body['params']
            if 'id' not in params or 'reason' not in params:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            id = params['id']
            reason = int(params['reason'])
            if not PaymeModel.objects.filter(paycom_transaction_id=id).exists():
                error_response = {
                    "error": {
                        "code": -31003,
                        "message": "Транзакция не найдена.",
                    }
                }
                return JsonResponse(error_response)
            payme = get_object_or_404(PaymeModel, paycom_transaction_id=id)
            if payme.status_payment == 1:
                payme.status_payment = -1
                payme.reason = reason
                payme.cancel_time = timezone.now()
                cancel_time = datetime.timestamp(payme.cancel_time) * 1000
                payme.save()
                error_response = {
                    "result": {
                        "transaction": f"{payme.id}",
                        "cancel_time": cancel_time,
                        "state": payme.status_payment
                    }
                }
                return JsonResponse(error_response)
            else:
                if payme.status_payment == 2:
                    error_response = {
                        "error": {
                            "code": -31007,
                            "message": "Невозможно отменить транзакцию. Товар или услуга предоставлена потребителю в полном объеме.",
                        },
                    }
                    return JsonResponse(error_response)
                else:
                    cancel_time = datetime.timestamp(payme.cancel_time) * 1000
                    error_response = {
                        "result": {
                            "transaction": f"{payme.id}",
                            "cancel_time": cancel_time,
                            "state": payme.status_payment
                        }
                    }
                    return JsonResponse(error_response)
        elif method == 'GetStatement':
            transactions = []
            if 'params' not in body:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            params = body['params']
            if 'from' not in params or 'to' not in params:
                error_response = {
                    "error": {
                        "code": -32600,
                        "message": "В RPC-запросе отсутствуют обязательные поля или тип полей не соответствует спецификации.",
                    }
                }
                return JsonResponse(error_response)
            from_time = int(params['from']) / 1000
            to_time = int(params['to']) / 1000
            fromtimemain = datetime.fromtimestamp(from_time)
            totimemain = datetime.fromtimestamp(to_time)
            payme = PaymeModel.objects.filter(create_time__isnull=False, create_time__gte=fromtimemain,
                                              create_time__lte=totimemain).order_by('create_time')
            for a in payme:
                if a.create_time is None:
                    create_time = 0
                else:
                    create_time = datetime.timestamp(a.create_time) * 1000
                if a.perform_time is None:
                    perform_time = 0
                else:
                    perform_time = datetime.timestamp(a.perform_time) * 1000
                if a.cancel_time is None:
                    cancel_time = 0
                else:
                    cancel_time = datetime.timestamp(a.cancel_time) * 1000
                ino = {
                    "id": f"{a.paycom_transaction_id}",
                    "time": create_time,
                    "amount": a.amount * 100,
                    "account": {
                        "phone": f"{a.user.profile.phone}",
                        "course_id": f"{a.course.id}",
                        "order_id": f"{a.id}",
                    },
                    "create_time": create_time,
                    "perform_time": perform_time,
                    "cancel_time": cancel_time,
                    "transaction": f"{a.id}",
                    "state": a.status_payment,
                    "reason": a.reason,
                }
                transactions.append(ino)
            error_response = {
                "result": {
                    "transactions": transactions
                }
            }
            return JsonResponse(error_response)
    else:
        error_response = {
            "error": {
                "code": -32300,
                "message": "Метод запроса не POST.",
            },
        }
        return JsonResponse(error_response)


class StatisticsCoursesListView(ListAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    queryset = CourseModel.objects.filter(active=True)
    serializer_class = StatisticsCoursesSerializer


class StatisticsLessonsListView(ListAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = StatisticsLessonsSerializer

    def get_queryset(self):
        return LessonModel.objects.filter(course_id=self.kwargs['id'], active=True).order_by('created_at')


class StatisticsTheoryTestView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = StatisticsTheoryTestSerializer
    queryset = LessonModel.objects.filter(active=True)
    lookup_url_kwarg = 'id'


class StatisticsTheoryDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = StatisticsTheoryDetailSerializer
    queryset = TheoryModel.objects.all()
    lookup_url_kwarg = 'id'


class StatisticsTestDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = StatisticsTestDetailSerializer
    queryset = TestModel.objects.all()
    lookup_url_kwarg = 'id'


class StatisticsUsersListView(ListAPIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    serializer_class = StatisticsUsersSerializer

    def get_queryset(self):
        ubm = UserBoughtCourseModel.objects.filter(trial=False, status=True)
        return UserModel.objects.filter(userboughtcoursemodel__isnull=False, userboughtcoursemodel__in=ubm).order_by(
            'first_name', 'last_name')


class StatisticsUsersDetailView(RetrieveAPIView):
    serializer_class = StatUserDetailSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def get_object(self):
        ubm = UserBoughtCourseModel.objects.filter(trial=False, course__active=True)
        return get_object_or_404(UserModel, id=self.kwargs['id'], userboughtcoursemodel__isnull=False,
                                 userboughtcoursemodel__in=ubm)


class StatisticsUserCourseDetailView(RetrieveAPIView):
    serializer_class = StatisticsUserCourseSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def get_object(self):
        return get_object_or_404(UserBoughtCourseModel, id=self.kwargs['id'], trial=False)


class StatisticsUserLessonDetailView(RetrieveAPIView):
    serializer_class = StatisticsUserLessonSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def get_object(self):
        return get_object_or_404(UserLessonModel, id=self.kwargs['id'], lesson__active=True)


class StatisticsUserTheoryDetailView(RetrieveAPIView):
    serializer_class = StatisticsUserTheorySerializer
    permission_classes = [IsAuthenticated, AdminPermission]
    queryset = UserTheoryModel.objects.all()
    lookup_url_kwarg = 'id'


class StatisticsUserTheoryDetailView(RetrieveAPIView):
    serializer_class = StatisticsUserTestSerializer
    permission_classes = [IsAuthenticated, AdminPermission]
    queryset = UserTestModel.objects.all()
    lookup_url_kwarg = 'id'
