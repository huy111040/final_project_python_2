from django.contrib import admin

from apps.courses.models import CourseClass, Semester, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits')
    search_fields = ('code', 'name')


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


@admin.register(CourseClass)
class CourseClassAdmin(admin.ModelAdmin):
    list_display = ('subject', 'lecturer', 'semester', 'room', 'schedule')
    list_filter = ('semester', 'subject')
    search_fields = ('subject__name', 'lecturer__username')
