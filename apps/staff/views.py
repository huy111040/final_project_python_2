from django.shortcuts import render
from apps.users.models import User
from apps.courses.models import StudentClass, Subject, Semester, CourseClass
from apps.enrollments.models import Enrollment

# Create your views here.
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