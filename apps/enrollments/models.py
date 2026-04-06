from django.db import models
from apps.users.models import User
from apps.courses.models import CourseClass, Semester

class Enrollment(models.Model):
    student = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'},
        related_name='enrollments',
        verbose_name="Sinh viên"
    )
    course_class = models.ForeignKey(
        CourseClass,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Lớp học phần"
    )

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