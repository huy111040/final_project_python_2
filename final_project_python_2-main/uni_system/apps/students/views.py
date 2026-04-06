from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.enrollments.models import Enrollment


@login_required(login_url='/')
def student_dashboard(request):
    return render(request, 'student/dashboard.html', {'user': request.user})


@login_required(login_url='/')
def student_schedule(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course_class__subject',
                                                                                 'course_class__lecturer')
    return render(request, 'student/schedule.html', {'enrollments': enrollments, 'user': request.user})


@login_required(login_url='/')
def student_grades(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course_class__subject')
    return render(request, 'student/grades.html', {'enrollments': enrollments, 'user': request.user})
