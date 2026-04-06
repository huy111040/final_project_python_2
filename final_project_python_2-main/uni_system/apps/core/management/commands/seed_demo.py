"""
Tạo dữ liệu mẫu khi admin / các bảng đang trống (sau migrate hoặc DB mới).
Chạy: python manage.py seed_demo
"""

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from apps.courses.models import CourseClass, Semester, Subject
from apps.enrollments.models import Enrollment
from apps.users.models import StudentClass, User


class Command(BaseCommand):
    help = 'Tạo tài khoản demo + học kỳ/môn/lớp mẫu (an toàn khi chạy lại: get_or_create)'

    def handle(self, *args, **options):
        # --- Tài khoản (khớp gợi ý trong note.txt) ---
        users_spec = [
            {'username': 'admin', 'password': '12345', 'role': 'ADMIN', 'user_code': 'ADM01',
             'first_name': 'Quản', 'last_name': 'Trị Viên'},
            {'username': 'giaovu_01', 'password': 'abc.12345', 'role': 'STAFF', 'user_code': 'GVU01',
             'first_name': 'Giáo', 'last_name': 'Vụ Một'},
            {'username': 'giangvien_01', 'password': 'abc.12345', 'role': 'LECTURER', 'user_code': 'GV001',
             'first_name': 'Giảng', 'last_name': 'Viên Một'},
            {'username': 'sinhvien_001', 'password': 'abc.12345', 'role': 'STUDENT', 'user_code': 'IT001',
             'first_name': 'Sinh', 'last_name': 'Viên Một'},
        ]

        for spec in users_spec:
            u, created = User.objects.get_or_create(
                username=spec['username'],
                defaults={
                    'password': make_password(spec['password']),
                    'role': spec['role'],
                    'user_code': spec['user_code'],
                    'first_name': spec['first_name'],
                    'last_name': spec['last_name'],
                    'email': f"{spec['username']}@example.edu",
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Tạo user: {u.username} ({spec['role']})"))
            else:
                self.stdout.write(f"  = Đã có user: {u.username}")

        # Quyền admin Django: chỉ superuser mới thấy toàn bộ app. Giáo vụ (staff) cần quyền từng model.
        self._ensure_admin_and_staff_permissions()

        sc, _ = StudentClass.objects.get_or_create(
            name='IT24A',
            defaults={'major': 'Công nghệ thông tin'},
        )
        sv = User.objects.filter(username='sinhvien_001').first()
        if sv and sv.student_class_id is None:
            sv.student_class = sc
            sv.save(update_fields=['student_class'])
            self.stdout.write(self.style.SUCCESS(f"  + Gán sinhvien_001 → lớp {sc.name}"))

        sem, created = Semester.objects.get_or_create(
            name='Học kỳ 1 (2024–2025)',
            defaults={'is_active': True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  + Học kỳ: {sem.name}"))

        sub, created = Subject.objects.get_or_create(
            code='PY101',
            defaults={'name': 'Lập trình Python', 'credits': 3},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  + Môn: {sub.code}"))

        lecturer = User.objects.filter(username='giangvien_01').first()
        cc = None
        if lecturer and sub and sem:
            cc, created = CourseClass.objects.get_or_create(
                subject=sub,
                semester=sem,
                lecturer=lecturer,
                defaults={
                    'room': 'A101',
                    'schedule': 'Thứ 2 (Sáng: Tiết 1-3)',
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Lớp học phần: {cc}"))

        if sv and cc:
            enr, created = Enrollment.objects.get_or_create(student=sv, course_class=cc)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Đăng ký: {sv.username} → {cc.subject.code}"))

        self.stdout.write(self.style.SUCCESS('\nXong. Đăng nhập admin đầy đủ quyền: username admin / mật khẩu 12345'))
        self.stdout.write('Tài khoản giaovu_01 cũng xem/sửa được toàn bộ bảng trong admin (đã gán quyền).')

    def _ensure_admin_and_staff_permissions(self):
        admin = User.objects.filter(username='admin').first()
        if admin:
            admin.role = 'ADMIN'
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ admin: is_superuser=True (thấy hết mục trong /admin/)'))

        gvu = User.objects.filter(username='giaovu_01').first()
        if gvu:
            gvu.role = 'STAFF'
            gvu.is_staff = True
            gvu.is_superuser = False
            gvu.user_permissions.set(Permission.objects.all())
            gvu.save()
            self.stdout.write(self.style.SUCCESS('  ✓ giaovu_01: đã gán toàn bộ quyền model (không còn trang admin trống).'))
