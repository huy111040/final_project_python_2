from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import StudentClass, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'user_code', 'email', 'first_name', 'last_name', 'role', 'student_class', 'is_staff')
    list_filter = ('role', 'student_class', 'is_staff', 'is_superuser', 'is_active')

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
