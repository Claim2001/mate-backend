from django.contrib import admin
from courses.models import *


@admin.register(TeacherModel)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'description', 'user']
    search_fields = ['full_name', ]
    ordering = ['-full_name']


@admin.register(CourseTipsModel)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['tip', 'sub_tip']
    search_fields = ['tip', 'sub_tip']
    ordering = ['-tip']


@admin.register(CourseModel)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration', 'price', 'active', 'author', 'teacher']
    list_filter = ['created_at', 'active']
    list_editable = ['active']
    search_fields = ['title', 'author']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tag', 'mentor')
    ordering = ['-title']


@admin.register(RequestModel)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'age', 'course', 'processed', 'phone']
    list_filter = ['course', 'processed', ]
    list_editable = ['processed']
    ordering = ['-created_at']


@admin.register(FeedbackModel)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'description', ]
    search_fields = ['full_name', 'description', ]
    ordering = ['-full_name']


@admin.register(SliderMainModel)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    ordering = ['-title']


@admin.register(SliderChildModel)
class SliderChildAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    ordering = ['-title']


@admin.register(LessonModel)
class LessonModelAdmin(admin.ModelAdmin):
    list_display = ['course', 'title', 'activation_day', 'author', 'active', 'lab_percentage', 'test_percentage']
    search_fields = ['course__title', 'title', 'activation_day', 'author__username', 'active', 'lab_percentage',
                     'test_percentage']
    ordering = ['-course', '-created_at']
    list_editable = ['activation_day', 'active']


@admin.register(TheoryModel)
class TheoryModelAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'title', 'author']
    search_fields = ['lesson__title', 'title', 'author__username']
    ordering = ['-lesson__course', '-lesson__created_at', '-created_at']
    list_select_related = True


@admin.register(TheoryIntroModel)
class TheoryIntroModelAdmin(admin.ModelAdmin):
    list_display = ['theory', 'title', 'text', 'author']
    search_fields = ['theory__title', 'title', 'text', 'author__username']
    ordering = ['-theory__lesson__course', '-theory__lesson__created_at', '-theory__created_at']
    list_select_related = True


@admin.register(TheoryChapterModel)
class TheoryChapterModelAdmin(admin.ModelAdmin):
    list_display = ['theory', 'title', 'text', 'author']
    search_fields = ['theory__title', 'title', 'text', 'author__username']
    ordering = ['-theory__lesson__course', '-theory__lesson__created_at', '-theory__created_at', '-created_at']
    list_select_related = True


@admin.register(TheoryLabChapterModel)
class TheoryLabChapterModelAdmin(admin.ModelAdmin):
    list_display = ['theory', 'title', 'embed', 'author', 'minimum_points', 'control']
    search_fields = ['theory__title', 'title', 'embed', 'author__username', 'minimum_points', 'control']
    ordering = ['-theory__lesson__course', '-theory__lesson__created_at', '-theory__created_at', '-created_at']
    list_select_related = True


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'title', 'author', 'minimum_percentage', 'control']
    search_fields = ['lesson__title', 'title', 'author__username', 'minimum_percentage', 'control']
    ordering = ['-lesson__course', '-lesson__created_at', '-created_at']
    list_select_related = True


@admin.register(TestIntroModel)
class TestIntroModelAdmin(admin.ModelAdmin):
    list_display = ['test', 'title', 'text', 'author']
    search_fields = ['test__title', 'title', 'text', 'author__username']
    ordering = ['-test__lesson__course', '-test__lesson__created_at', '-test__created_at']
    list_select_related = True


@admin.register(TestChapterModel)
class TestChapterModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'test', 'type', 'question', 'feedback_true', 'feedback_false', 'short_answer', 'author']
    search_fields = ['test__title', 'title', 'type', 'question', 'feedback_true', 'feedback_false', 'short_answer',
                     'author__username']
    ordering = ['-test__lesson__course', '-test__lesson__created_at', '-test__created_at', '-created_at']
    list_select_related = True


@admin.register(TestVariantModel)
class TestVariantModelAdmin(admin.ModelAdmin):
    list_display = ['test_chapter', 'answer', 'variant']
    search_fields = ['test_chapter__title', 'answer__username', 'variant']
    ordering = ['-test_chapter__test__lesson__course', '-test_chapter__test__lesson__created_at',
                '-test_chapter__test__created_at', '-test_chapter__created_at', '-variant']
    list_select_related = True


@admin.register(UserBoughtCourseModel)
class UserBoughtCourseModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'bought_date', 'expiration_date', 'gpa']
    search_fields = ['user__username', 'course__title_lms', 'status', 'bought_date', 'expiration_date']
    list_editable = ['status']
    ordering = ['-user__username', '-course__title']
    list_select_related = True


@admin.register(UserGPAHistory)
class UserGPAHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_course', 'gpa']
    search_fields = ['user_course__course__title_lms', 'user_course__user__username', 'gpa']
    ordering = ['-user_course__user__username', '-user_course__course__title', '-created_at']
    list_select_related = True


@admin.register(UserLessonModel)
class UserLessonModelAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'available', 'user', 'done', 'activation_date', 'gpa']
    search_fields = ['lesson__title', 'available', 'user__username', 'done', 'activation_date']
    ordering = ['-user', '-lesson__course', '-lesson__created_at']
    list_select_related = True


@admin.register(UserLessonOverallModel)
class UserLessonOverallModelAdmin(admin.ModelAdmin):
    list_display = ['user_lesson', 'available', 'seen']
    search_fields = ['user_lesson__lesson__title', 'user_lesson__user__username', 'available', 'seen']
    ordering = ['-user_lesson__user', '-user_lesson__lesson__course', '-user_lesson__lesson__created_at']
    list_select_related = True


@admin.register(UserGotLessonOverallModel)
class UserGotLessonOverallModelAdmin(admin.ModelAdmin):
    list_display = ['user_overall', 'points']
    search_fields = ['-user_overall__user_lesson__user__username', '-user_overall__user_lesson__lesson__title',
                     'points']
    ordering = ['-user_overall__user_lesson__user', '-user_overall__user_lesson__lesson__course',
                '-user_overall__user_lesson__lesson__created_at']
    list_select_related = True


@admin.register(UserTheoryModel)
class UserTheoryModelAdmin(admin.ModelAdmin):
    list_display = ['theory', 'user', 'created_at', 'available', 'seen', 'done']
    search_fields = ['theory__title', 'user__username', 'created_at', 'available', 'seen', 'done']
    ordering = ['-user', '-theory__lesson__course', '-theory__lesson__created_at', '-theory__created_at', '-created_at']
    list_select_related = True


@admin.register(UserTheoryIntroModel)
class UserTheoryIntroModelAdmin(admin.ModelAdmin):
    list_display = ['theory_intro', 'user', 'available', 'seen', 'done']
    search_fields = ['theory_intro__title', 'user__username', 'available', 'seen', 'done']
    ordering = ['-user', '-theory_intro__theory__lesson__course', '-theory_intro__theory__lesson__created_at',
                '-theory_intro__theory__created_at', '-theory_intro__created_at', '-created_at']
    list_select_related = True


@admin.register(UserTheoryChapterModel)
class UserTheoryChapterModelAdmin(admin.ModelAdmin):
    list_display = ['theory_chapter', 'user', 'available', 'seen', 'done']
    search_fields = ['theory_chapter__title', 'user__username', 'available', 'seen', 'done']
    ordering = ['-user', '-theory_chapter__theory__lesson__course', '-theory_chapter__theory__lesson__created_at',
                '-theory_chapter__theory__created_at', '-theory_chapter__created_at', '-created_at']
    list_select_related = True


@admin.register(UserTheoryLabModel)
class UserTheoryLabModelAdmin(admin.ModelAdmin):
    list_display = ['theory_lab', 'user', 'available', 'seen', 'done']
    search_fields = ['theory_lab__title', 'user__username', 'available', 'seen', 'done']
    ordering = ['-user', '-theory_lab__theory__lesson__course', '-theory_lab__theory__lesson__created_at',
                '-theory_lab__theory__created_at', '-theory_lab__created_at', '-created_at']
    list_select_related = True


@admin.register(UserAnsweredTheoryLabModel)
class UserAnsweredTheoryLabModelAdmin(admin.ModelAdmin):
    list_display = ['user_theory_lab', 'points', 'comment', 'enough']
    search_fields = ['-user_theory_lab__user__username', '-user_theory_lab__theory_lab__title',
                     'points', 'comment']
    ordering = ['-user_theory_lab__user', '-user_theory_lab__theory_lab__theory__lesson__course',
                '-user_theory_lab__theory_lab__theory__lesson__created_at',
                '-user_theory_lab__theory_lab__theory__created_at', '-user_theory_lab__theory_lab__created_at',
                '-user_theory_lab__created_at', '-created_at']
    list_select_related = True


@admin.register(UserTestModel)
class UserTestModelAdmin(admin.ModelAdmin):
    list_display = ['test', 'user', 'available', 'seen', 'done']
    search_fields = ['test__title', 'user__username', 'available', 'seen', 'done']
    ordering = ['-user', '-test__lesson__course', '-test__lesson__created_at', '-test__created_at', '-created_at']
    list_select_related = True


@admin.register(UserAnsweredTestModel)
class UserAnsweredTestModelAdmin(admin.ModelAdmin):
    list_display = ['user_test_model', 'points', 'enough']
    search_fields = ['-user_test_model__user__username', '-user_test_model__test__title', 'points', 'enough']
    ordering = ['-user_test_model__user', '-user_test_model__test__lesson__course',
                '-user_test_model__test__lesson__created_at', '-user_test_model__test__created_at',
                '-user_test_model__created_at', '-created_at']
    list_select_related = True


@admin.register(UserTestIntroModel)
class UserTestIntroModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'test_intro', 'available', 'seen', 'done']
    search_fields = ['user__username', 'test_intro__title', 'available', 'seen', 'done']
    ordering = ['-user', '-test_intro__test__lesson__course', '-test_intro__test__lesson__created_at',
                '-test_intro__test__created_at', '-test_intro__created_at', '-created_at']
    list_select_related = True


@admin.register(UserTestChapterModel)
class UserTestChapterModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'test_chapter', 'available', 'seen', 'done']
    search_fields = ['user__username', 'test_chapter__title', 'available', 'seen', 'done']
    ordering = ['-user', '-test_chapter__test__lesson__course', '-test_chapter__test__lesson__created_at',
                '-test_chapter__test__created_at', '-test_chapter__created_at', '-created_at']
    list_select_related = True


@admin.register(UserAnsweredTestChapterModel)
class UserAnsweredTestChapterModelAdmin(admin.ModelAdmin):
    list_display = ['user_test', 'correct']
    search_fields = ['-user_test__user__username', '-user_test__test_chapter__title', 'correct']
    ordering = ['-user_test__user', '-user_test__test_chapter__test__lesson__course',
                '-user_test__test_chapter__test__lesson__created_at', '-user_test__test_chapter__test__created_at',
                '-user_test__test_chapter__created_at', '-user_test__created_at', '-created_at']
    list_select_related = True


@admin.register(TagModel)
class TagModelAdmin(admin.ModelAdmin):
    list_display = ['tag']
    search_fields = ['tag']
    ordering = ['-tag']


@admin.register(EditorImageModel)
class EditorImageModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']
    search_fields = ['tag']
    ordering = ['-image']
