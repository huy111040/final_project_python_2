from django.shortcuts import render
from apps.users.models import User
from apps.courses.models import StudentClass, Subject, Semester, CourseClass
from apps.enrollments.models import Enrollment


# Create your views here.
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
