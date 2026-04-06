from django.conf import settings
from django.db import models


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Mã môn")
    name = models.CharField(max_length=100, verbose_name="Tên môn")
    credits = models.IntegerField(verbose_name="Số tín chỉ")

    class Meta:
        db_table = 'core_subject'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    name = models.CharField(max_length=50, verbose_name="Tên học kỳ")
    is_active = models.BooleanField(default=False, verbose_name="Đang diễn ra")

    class Meta:
        db_table = 'core_semester'

    def __str__(self):
        return self.name


class CourseClass(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='classes', verbose_name="Môn học")
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'LECTURER'},
        related_name='teaching_classes',
        verbose_name="Giảng viên",
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='classes', verbose_name="Học kỳ")
    room = models.CharField(max_length=50, verbose_name="Phòng học")
    schedule = models.CharField(max_length=100, verbose_name="Lịch học")

    class Meta:
        db_table = 'core_courseclass'

    def __str__(self):
        lecturer_name = self.lecturer.get_full_name() if self.lecturer else "Chưa phân công"
        return f"{self.subject.name} - {lecturer_name} ({self.semester.name})"
