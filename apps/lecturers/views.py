from django.shortcuts import render
from apps.users.models import User
from apps.courses.models import StudentClass, Subject, Semester, CourseClass
from apps.enrollments.models import Enrollment

# Create your views here.
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
