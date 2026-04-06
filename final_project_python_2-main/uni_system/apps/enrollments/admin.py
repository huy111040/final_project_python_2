from django.contrib import admin

from apps.courses.models import CourseClass
from apps.enrollments.models import Enrollment


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 3


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_class', 'attendance_score', 'midterm_score', 'final_score')
    list_filter = ('course_class__semester', 'course_class__subject')
    search_fields = ('student__user_code', 'student__username')


# Gắn inline đăng ký vào Lớp học phần (đăng ký ở app enrollments để tránh import vòng)
class CourseClassAdminWithEnrollments(admin.ModelAdmin):
    list_display = ('subject', 'lecturer', 'semester', 'room', 'schedule')
    list_filter = ('semester', 'subject')
    search_fields = ('subject__name', 'lecturer__username')
    inlines = [EnrollmentInline]


admin.site.unregister(CourseClass)
admin.site.register(CourseClass, CourseClassAdminWithEnrollments)
