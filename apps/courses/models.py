from django.db import models
from apps.users.models import User

class StudentClass(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tên lớp sinh hoạt")
    major = models.CharField(max_length=100, null=True, blank=True, verbose_name="Chuyên ngành")

    def __str__(self):
        return self.name

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Mã môn")
    name = models.CharField(max_length=100, verbose_name="Tên môn")
    credits = models.IntegerField(verbose_name="Số tín chỉ")

    def __str__(self):
        return f"{self.code} - {self.name}"

class Semester(models.Model):
    name = models.CharField(max_length=50, verbose_name="Tên học kỳ")
    is_active = models.BooleanField(default=False, verbose_name="Đang diễn ra")

    def __str__(self):
        return self.name

class CourseClass(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='classes', verbose_name="Môn học")
    lecturer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'LECTURER'},
        related_name='teaching_classes',
        verbose_name="Giảng viên"
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='classes', verbose_name="Học kỳ")
    room = models.CharField(max_length=50, verbose_name="Phòng học")
    schedule = models.CharField(max_length=100, verbose_name="Lịch học")

    def __str__(self):
        lecturer_name = self.lecturer.get_full_name() if self.lecturer else "Chưa phân công"
        return f"{self.subject.name} - {lecturer_name} ({self.semester.name})"