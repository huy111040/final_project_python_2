from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subject, Semester, CourseClass, Enrollment, StudentClass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Thêm 'student_class' vào list_display và list_filter
    list_display = ('username', 'user_code', 'email', 'first_name', 'last_name', 'role', 'student_class', 'is_staff')
    list_filter = ('role', 'student_class', 'is_staff', 'is_superuser', 'is_active')

    # Thêm 'student_class' vào fieldsets để có thể edit
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('role', 'user_code', 'student_class')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('role', 'user_code', 'student_class')}),
    )

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'major')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits')
    search_fields = ('code', 'name')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 3

@admin.register(CourseClass)
class CourseClassAdmin(admin.ModelAdmin):
    list_display = ('subject', 'lecturer', 'semester', 'room', 'schedule')
    list_filter = ('semester', 'subject')
    search_fields = ('subject__name', 'lecturer__username')
    inlines = [EnrollmentInline]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_class', 'attendance_score', 'midterm_score', 'final_score')
    list_filter = ('course_class__semester', 'course_class__subject')
    search_fields = ('student__user_code', 'student__username')