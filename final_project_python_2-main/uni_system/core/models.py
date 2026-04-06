from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group


class StudentClass(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tên lớp sinh hoạt")
    major = models.CharField(max_length=100, null=True, blank=True, verbose_name="Chuyên ngành")

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('STAFF', 'Giáo vụ'),
        ('LECTURER', 'Giảng viên'),
        ('STUDENT', 'Sinh viên'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='STUDENT', verbose_name="Vai trò")
    user_code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Mã số (SV/GV)")
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True,
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
        User,
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


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'},
                                related_name='enrollments', verbose_name="Sinh viên")
    course_class = models.ForeignKey(CourseClass, on_delete=models.CASCADE, related_name='enrollments',
                                     verbose_name="Lớp học phần")

    attendance_score = models.FloatField(null=True, blank=True, verbose_name="Điểm chuyên cần")
    regular_score = models.FloatField(null=True, blank=True, verbose_name="Điểm thường xuyên")  # Thêm cột này
    midterm_score = models.FloatField(null=True, blank=True, verbose_name="Điểm giữa kỳ")
    final_score = models.FloatField(null=True, blank=True, verbose_name="Điểm cuối kỳ")

    # Thuộc tính ảo để tự động tính Điểm TBM mà không cần lưu cứng vào DB
    @property
    def average_score(self):
        # Kiểm tra xem giảng viên đã nhập ĐỦ 4 cột điểm chưa
        scores = [self.attendance_score, self.regular_score, self.midterm_score, self.final_score]
        if all(score is not None for score in scores):
            avg = (self.attendance_score * 0.15) + (self.regular_score * 0.15) + (self.midterm_score * 0.20) + (
                    self.final_score * 0.50)
            return round(avg, 2)
        return None  # Nếu thiếu điểm thì trả về None

    @property
    def letter_grade(self):
        avg = self.average_score
        if avg is None: return None
        if avg >= 8.5:
            return 'A'
        elif avg >= 7.0:
            return 'B'
        elif avg >= 5.5:
            return 'C'
        elif avg >= 4.0:
            return 'D'
        else:
            return 'F'

    @property
    def gpa_4(self):
        avg = self.average_score
        if avg is None: return None
        if avg >= 8.5:
            return 4.0
        elif avg >= 7.0:
            return 3.0
        elif avg >= 5.5:
            return 2.0
        elif avg >= 4.0:
            return 1.0
        else:
            return 0.0

    class Meta:
        unique_together = ('student', 'course_class')
        verbose_name = "Bảng điểm / Đăng ký"
        verbose_name_plural = "Bảng điểm / Đăng ký"

    def __str__(self):
        return f"{self.student.user_code} - {self.course_class.subject.name}"


@receiver(post_save, sender=User)
def assign_role_group(sender, instance, created, **kwargs):
    if created:  # Chỉ chạy khi tài khoản mới được tạo
        # Lấy tên hiển thị của Role (vd: 'Giáo vụ', 'Sinh viên')
        role_name = dict(User.ROLE_CHOICES).get(instance.role)
        if role_name:
            # Tìm Group có tên này trong DB, nếu chưa có thì tự động tạo mới
            group, _ = Group.objects.get_or_create(name=role_name)
            instance.groups.add(group)
