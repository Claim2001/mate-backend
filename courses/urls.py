from django.urls import path
from courses.views import CourseListView, CourseDetailView, RequestCreateView, FeedbackListView, SliderListView, \
    UserBoughtCourseCreateView, UserBoughtCourseListView, CourseCreateView, LessonCreateView, TheoryCreateView, \
    TestCreateView, TheoryIntroCreateView, TheoryChapterCreateView, TheoryLabCreateView, TestIntroCreateView, \
    TestChapterCreateView, LessonUpdateDeleteView, TheoryUpdateDeleteView, StudentLessonListView, \
    StudentLessonDetailView, LessonListView, LessonDetailView, TheoryDetailView, TestDetailView, \
    StudentTheoryDetailView, StudentTheoryIntroDetailView, CourseAvailableListView, StudentTheoryChapterDetailView, \
    StudentTheoryLabDetailView, StudentTestDetailView, CheckTheoryLabView, TeacherListView, StudentTestIntroDetailView, \
    CourseAdminDetailView, EditorImageCreateView, EditorImageDetailView, EditorParserView, \
    StudentTestChapterDetailView, StudentTestCurrentChapterView, StudentTestEndView, \
    TheoryIntroDetailUpdateDeleteView, StudentTestPointsDetailView, StudentLessonPointsView, CheckTheoryLabListView, \
    UserTrialCourseCreateView, UserAssignCourseCreateView, UserUnassignedCourseDestroyView, \
    TheoryChapterDetailUpdateDeleteView, TheoryLabDetailUpdateDeleteView, TestIntroDetailUpdateDeleteView, \
    TestChapterDetailUpdateView

urlpatterns = [
    path('course/create/', CourseCreateView.as_view(), name='course-create'),
    path('course/detail/<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('course/admin/detail/<int:id>/', CourseAdminDetailView.as_view(), name='course-detail'),
    path('course/list/', CourseListView.as_view(), name='course-list'),
    path('course/available/list/', CourseAvailableListView.as_view(), name='course-available-list'),
    path('course/bought/', UserBoughtCourseCreateView.as_view(), name='course-bought'),
    path('course/assign/', UserAssignCourseCreateView.as_view(), name='course-assign'),
    path('course/unassign/<int:id>/', UserUnassignedCourseDestroyView.as_view(), name='course-assign'),
    path('course/trial/', UserTrialCourseCreateView.as_view(), name='course-trial'),
    path('course/bought/list/', UserBoughtCourseListView.as_view(), name='course-bought-list'),
    path('lesson/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lesson/list/', LessonListView.as_view(), name='lesson-list'),
    path('lesson/detail/<int:id>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lesson/<int:id>/', LessonUpdateDeleteView.as_view(), name='lesson-update-delete'),
    path('theory/create/', TheoryCreateView.as_view(), name='theory-create'),
    path('theory/detail/<int:id>/', TheoryDetailView.as_view(), name='theory-detail'),
    path('theory/<int:id>/', TheoryUpdateDeleteView.as_view(), name='theory-update-delete'),
    path('theory/intro/create/', TheoryIntroCreateView.as_view(), name='theory-intro-create'),
    path('theory/intro/detail/<int:id>/', TheoryIntroDetailUpdateDeleteView.as_view(),
         name='theory-intro-detail-update-delete'),
    path('theory/chapter/create/', TheoryChapterCreateView.as_view(), name='theory-chapter-create'),
    path('theory/chapter/detail/<int:id>/', TheoryChapterDetailUpdateDeleteView.as_view(),
         name='theory-chapter-detail'),
    path('theory/lab/create/', TheoryLabCreateView.as_view(), name='theory-lab-create'),
    path('theory/lab/detail/<int:id>/', TheoryLabDetailUpdateDeleteView.as_view(), name='theory-lab-detail'),
    path('test/create/', TestCreateView.as_view(), name='test-create'),
    path('test/detail/<int:id>/', TestDetailView.as_view(), name='test-detail'),
    path('test/intro/create/', TestIntroCreateView.as_view(), name='test-intro-create'),
    path('test/intro/detail/<int:id>/', TestIntroDetailUpdateDeleteView.as_view(), name='test-intro-create'),
    path('test/chapter/create/', TestChapterCreateView.as_view(), name='test-chapter-create'),
    path('test/chapter/detail/<int:id>/', TestChapterDetailUpdateView.as_view(), name='test-chapter-create'),
    path('request/create/', RequestCreateView.as_view(), name='request-create'),
    path('feedback/list/', FeedbackListView.as_view(), name='feedback-list'),
    path('teacher/list/', TeacherListView.as_view(), name='teacher-list'),
    path('course/<slug:slug>/slider/list/', SliderListView.as_view(), name='slider-list'),
    path('student/lesson/list/', StudentLessonListView.as_view(), name='student-lesson-list'),
    path('student/lesson/detail/<int:id>/', StudentLessonDetailView.as_view(), name='student-lesson-detail'),
    path('student/lesson/points/<int:id>/', StudentLessonPointsView.as_view(), name='student-test-points'),
    path('student/theory/detail/<int:id>/', StudentTheoryDetailView.as_view(), name='student-theory-detail'),
    path('student/theory/intro/detail/<int:id>/', StudentTheoryIntroDetailView.as_view(),
         name='student-theory-intro-detail'),
    path('student/theory/chapter/detail/<int:id>/', StudentTheoryChapterDetailView.as_view(),
         name='student-theory-chapter-detail'),
    path('student/theory/lab/detail/<int:id>/', StudentTheoryLabDetailView.as_view(), name='student-theory-lab-detail'),
    path('student/test/detail/<int:id>/', StudentTestDetailView.as_view(), name='student-test-detail'),
    path('student/test/intro/detail/<int:id>/', StudentTestIntroDetailView.as_view(), name='student-test-intro-detail'),
    path('student/test/chapter/current/<int:id>/', StudentTestCurrentChapterView.as_view(),
         name='student-test-current-chapter'),
    path('student/test/chapter/detail/<int:id>/', StudentTestChapterDetailView.as_view(),
         name='student-test-chapter-detail'),
    path('student/test/points/<int:id>/', StudentTestPointsDetailView.as_view(), name='student-test-points'),
    path('mentor/theory/lab/list/', CheckTheoryLabListView.as_view(), name='mentor-theory-lab-list'),
    path('mentor/theory/lab/detail/<int:id>/', CheckTheoryLabView.as_view(), name='mentor-theory-lab'),
    path('test/end/<int:id>/', StudentTestEndView.as_view(), name='test-end'),
    path('editor/image/create/', EditorImageCreateView.as_view(), name='editor-image-create'),
    path('editor/image/detail/<int:id>/', EditorImageDetailView.as_view(), name='editor-image-detail'),
    path('editor/parser/', EditorParserView.as_view(), name='editor-parser'),
]
