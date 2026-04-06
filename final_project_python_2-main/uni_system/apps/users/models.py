from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class StudentClass(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tên lớp sinh hoạt")
    major = models.CharField(max_length=100, null=True, blank=True, verbose_name="Chuyên ngành")

    class Meta:
        db_table = 'core_studentclass'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Giữ db_table và bảng M2M cũ (core_*) để tương thích DB đã migrate từ app core."""

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
        db_table="core_user_groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_set",
        related_query_name="user",
        db_table="core_user_user_permissions",
    )

    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Giáo vụ'),
        ('LECTURER', 'Giảng viên'),
        ('STUDENT', 'Sinh viên'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='STUDENT', verbose_name="Vai trò")
    user_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Mã số (SV/GV)")
    student_class = models.ForeignKey(
        StudentClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Lớp sinh hoạt",
    )

    class Meta:
        db_table = 'core_user'

    def save(self, *args, **kwargs):
        if self.role in ['STAFF', 'ADMIN']:
            self.is_staff = True
        if self.role == 'ADMIN':
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_code or self.username} - {self.get_full_name()} ({self.get_role_display()})"
