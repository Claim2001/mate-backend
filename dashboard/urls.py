from django.urls import path

from dashboard.views import KnowledgeBaseCreateView, KnowledgeBaseListView, KnowledgeBaseDetailView, StatisticsView, \
    StatisticsMenuView, KnowledgeVideoCreateView, KnowledgeBookCreateView, \
    NotificationListView, HelpListView, ProfileDashboardView, OrderCreateView, PrepareView, paymeview, OrderPaymeView, \
    StatisticsCoursesListView, StatisticsLessonsListView, StatisticsTheoryTestView, StatisticsTheoryDetailView, \
    StatisticsTestDetailView, StatisticsUsersListView, StatisticsUsersDetailView, StatisticsUserCourseDetailView, \
    StatisticsUserLessonDetailView, StatisticsUserTheoryDetailView

urlpatterns = [
    path('order/payme/create/', OrderPaymeView.as_view(), name='order-payme-create'),
    path('payme/', paymeview, name='payme-create'),
    path('order/create/', OrderCreateView.as_view(), name='order-create'),
    path('prepare/create/', PrepareView.as_view(), name='perform-create'),
    path('base/create/', KnowledgeBaseCreateView.as_view(), name='base-create'),
    path('base/video/create/', KnowledgeVideoCreateView.as_view(), name='base-video-create'),
    path('base/book/create/', KnowledgeBookCreateView.as_view(), name='base-book-create'),
    path('base/list/', KnowledgeBaseListView.as_view(), name='base-list'),
    path('base/detail/<int:id>/', KnowledgeBaseDetailView.as_view(), name='base-detail'),
    path('profile/', ProfileDashboardView.as_view(), name='profile-dashboard'),
    path('statistics/menu/', StatisticsMenuView.as_view(), name='statistics-menu'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('statistics/courses/', StatisticsCoursesListView.as_view(), name='statistics-courses'),
    path('statistics/course/<int:id>/', StatisticsLessonsListView.as_view(), name='statistics-lessons'),
    path('statistics/lesson/<int:id>/', StatisticsTheoryTestView.as_view(), name='statistics-theory-test'),
    path('statistics/theory/<int:id>/', StatisticsTheoryDetailView.as_view(), name='statistics-theory-detail'),
    path('statistics/test/<int:id>/', StatisticsTestDetailView.as_view(), name='statistics-test-detail'),
    path('statistics/users/', StatisticsUsersListView.as_view(), name='statistics-users'),
    path('statistics/user/<int:id>/', StatisticsUsersDetailView.as_view(), name='statistics-user-detail'),
    path('statistics/user/course/<int:id>/', StatisticsUserCourseDetailView.as_view(), name='statistics-course-detail'),
    path('statistics/user/lesson/<int:id>/', StatisticsUserLessonDetailView.as_view(), name='statistics-lesson-detail'),
    path('statistics/user/theory/<int:id>/', StatisticsUserTheoryDetailView.as_view(), name='statistics-theory-detail'),
    path('statistics/user/test/<int:id>/', StatisticsUserTheoryDetailView.as_view(), name='statistics-test-detail'),
    path('notification/list/', NotificationListView.as_view(), name='notification-list'),
    path('help/list/', HelpListView.as_view(), name='help-list'),
]
