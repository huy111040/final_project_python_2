from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CourseClassForm, SubjectForm
from .models import Enrollment, CourseClass, User, StudentClass, Subject
from django.contrib.auth import update_session_auth_hash
from .forms import UserProfileForm

def login_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('username')
        pass_input = request.POST.get('password')

        user = authenticate(request, username=user_input, password=pass_input)

        if user is not None:
            login(request, user)
            if user.role == 'STUDENT':
                return redirect('student_dashboard')
            elif user.role == 'LECTURER':
                return redirect('lecturer_dashboard')
            elif user.role == 'STAFF':
                return redirect('staff_dashboard')
            else:
                return redirect('/admin/')
        else:
            return render(request, 'login.html', {'error_message': 'Sai tên đăng nhập hoặc mật khẩu!'})

    return render(request, 'login.html')

@login_required(login_url='/')
def user_profile(request):
    user = request.user
    profile_form = UserProfileForm(instance=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Xử lý Cập nhật thông tin
        if action == 'update_profile':
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Cập nhật thông tin cá nhân thành công!')
                return redirect('user_profile')

        # 2. Xử lý Đổi mật khẩu
        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not user.check_password(old_password):
                messages.error(request, 'Mật khẩu cũ không chính xác!')
            elif new_password != confirm_password:
                messages.error(request, 'Mật khẩu xác nhận không khớp!')
            elif len(new_password) < 6:
                messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự!')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user) # Giữ phiên đăng nhập
                messages.success(request, 'Đổi mật khẩu thành công!')
                return redirect('user_profile')

    return render(request, 'profile.html', {
        'profile_form': profile_form,
        'user': user
    })


@login_required(login_url='/')
def student_dashboard(request):
    # Chỉ hiển thị menu điều hướng, không cần truy vấn DB nặng
    return render(request, 'student/dashboard.html', {'user': request.user})


@login_required(login_url='/')
def student_schedule(request):
    # Chỉ truy vấn dữ liệu liên quan đến lịch học
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course_class__subject',
                                                                                 'course_class__lecturer')
    return render(request, 'student/schedule.html', {'enrollments': enrollments, 'user': request.user})


@login_required(login_url='/')
def student_grades(request):
    # Chỉ truy vấn dữ liệu liên quan đến điểm số
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course_class__subject')
    return render(request, 'student/grades.html', {'enrollments': enrollments, 'user': request.user})


@login_required(login_url='/')
def lecturer_dashboard(request):
    return render(request, 'lecturer/dashboard.html', {'user': request.user})


@login_required(login_url='/')
def lecturer_schedule(request):
    # Truy vấn các lớp học phần mà giảng viên này đang được phân công dạy
    classes = CourseClass.objects.filter(lecturer=request.user).select_related('subject', 'semester')
    return render(request, 'lecturer/schedule.html', {'classes': classes, 'user': request.user})


@login_required(login_url='/')
def lecturer_grade_select(request):
    # Lấy danh sách lớp giảng viên đang dạy để họ chọn
    classes = CourseClass.objects.filter(lecturer=request.user).select_related('subject', 'semester')
    return render(request, 'lecturer/grade_select.html', {'classes': classes, 'user': request.user})


@login_required(login_url='/')
def lecturer_grade_input(request, class_id):
    # Lấy thông tin lớp học, đảm bảo lớp này do chính giảng viên này dạy
    course_class = get_object_or_404(CourseClass, id=class_id, lecturer=request.user)

    # Lấy danh sách sinh viên trong lớp (từ bảng Enrollment)
    enrollments = Enrollment.objects.filter(course_class=course_class).select_related('student')

    if request.method == 'POST':
        # Duyệt qua từng sinh viên để lấy điểm từ Form gửi lên
        for e in enrollments:
            att = request.POST.get(f'attendance_{e.id}')
            reg = request.POST.get(f'regular_{e.id}')
            mid = request.POST.get(f'midterm_{e.id}')
            fin = request.POST.get(f'final_{e.id}')

            # Cập nhật nếu có nhập số, nếu bỏ trống thì bỏ qua
            if att: e.attendance_score = float(att)
            if reg: e.regular_score = float(reg)
            if mid: e.midterm_score = float(mid)
            if fin: e.final_score = float(fin)
            e.save()

        # 1. TẠO THÔNG BÁO SAU KHI LƯU THÀNH CÔNG
        messages.success(request, 'Đã cập nhật bảng điểm thành công!')

        # Lưu xong tải lại trang hiện tại (lúc này request chuyển thành GET)
        return redirect('lecturer_grade_input', class_id=class_id)

    # 2. TRUYỀN THÔNG BÁO RA GIAO DIỆN (Bắt buộc phải có dòng 'messages' này)
    return render(request, 'lecturer/grade_input.html', {
        'course_class': course_class,
        'enrollments': enrollments,
        'user': request.user,
        'messages': messages.get_messages(request)
    })


# Cập nhật hàm staff_dashboard
@login_required(login_url='/')
def staff_dashboard(request):
    # Bảo vệ: Chỉ cho phép Giáo vụ truy cập
    if getattr(request.user, 'role', '') != 'STAFF':
        return redirect('login')

    # 1. Lấy dữ liệu thống kê tổng quan
    total_students = User.objects.filter(role='STUDENT').count()
    total_lecturers = User.objects.filter(role='LECTURER').count()
    total_subjects = Subject.objects.count()
    total_classes = CourseClass.objects.count()

    # 2. Chỉ lấy 5 lớp học phần mới nhất để hiển thị cho gọn
    recent_classes = CourseClass.objects.select_related(
        'subject', 'lecturer', 'semester'
    ).order_by('-id')[:5]

    return render(request, 'staff/dashboard.html', {
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_subjects': total_subjects,
        'total_classes': total_classes,
        'recent_classes': recent_classes,
        'user': request.user
    })


@login_required(login_url='/')
def staff_manage_enrollment(request, class_id):
    course_class = get_object_or_404(CourseClass, id=class_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_cohort':
            cohort_id = request.POST.get('cohort_id')
            students = User.objects.filter(role='STUDENT', student_class_id=cohort_id)
            for student in students:
                Enrollment.objects.get_or_create(student=student, course_class=course_class)
        elif action == 'add_individual':
            student_id = request.POST.get('student_id')
            student = get_object_or_404(User, id=student_id, role='STUDENT')
            Enrollment.objects.get_or_create(student=student, course_class=course_class)
        elif action == 'remove':
            enrollment_id = request.POST.get('enrollment_id')
            Enrollment.objects.filter(id=enrollment_id).delete()
        return redirect('staff_manage_enrollment', class_id=class_id)

    cohorts = StudentClass.objects.all()
    enrollments = Enrollment.objects.filter(course_class=course_class).select_related('student__student_class')
    enrolled_student_ids = enrollments.values_list('student_id', flat=True)
    available_students = User.objects.filter(role='STUDENT').exclude(id__in=enrolled_student_ids)

    return render(request, 'staff/manage_enrollment.html', {
        'course_class': course_class, 'cohorts': cohorts,
        'available_students': available_students, 'enrollments': enrollments, 'user': request.user
    })


@login_required(login_url='/')
def staff_courseclass_add(request):
    # Bảo mật: Chỉ giáo vụ mới được vào trang này
    if request.user.role != 'STAFF':
        return redirect('login')

    if request.method == 'POST':
        form = CourseClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Lớp học phần mới thành công!')
            return redirect('staff_dashboard')  # Tạo xong quay về dashboard
    else:
        form = CourseClassForm()

    return render(request, 'staff/courseclass_add.html', {
        'form': form,
        'user': request.user
    })

@login_required(login_url='/')
def staff_subject_add(request):
    if getattr(request.user, 'role', '') != 'STAFF':
        return redirect('login')

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm môn học mới thành công!')
            return redirect('staff_dashboard') # Tạm thời lưu xong quay về Dashboard
    else:
        form = SubjectForm()

    return render(request, 'staff/subject_add.html', {
        'form': form,
        'user': request.user
    })


@login_required(login_url='/')
def staff_courseclass_list(request):
    if getattr(request.user, 'role', '') != 'STAFF':
        return redirect('login')

    # Lấy toàn bộ danh sách lớp học phần
    course_classes = CourseClass.objects.select_related('subject', 'lecturer', 'semester').all().order_by('-id')

    return render(request, 'staff/courseclass_list.html', {
        'course_classes': course_classes,
        'user': request.user
    })