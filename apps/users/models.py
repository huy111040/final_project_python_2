from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Giáo vụ'),
        ('LECTURER', 'Giảng viên'),
        ('STUDENT', 'Sinh viên'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='STUDENT', verbose_name="Vai trò")
    user_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Mã số (SV/GV)")
    student_class = models.ForeignKey('courses.StudentClass', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='students', verbose_name="Lớp sinh hoạt")

    def save(self, *args, **kwargs):
        # Tự động cấp quyền đăng nhập trang Admin cho Giáo vụ và Admin
        if self.role in ['STAFF', 'ADMIN']:
            self.is_staff = True
        if self.role == 'ADMIN':
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_code or self.username} - {self.get_full_name()} ({self.get_role_display()})"
