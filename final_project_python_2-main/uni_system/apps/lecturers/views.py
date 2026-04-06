from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.courses.models import CourseClass
from apps.enrollments.models import Enrollment


@login_required(login_url='/')
def lecturer_dashboard(request):
    return render(request, 'lecturer/dashboard.html', {'user': request.user})


@login_required(login_url='/')
def lecturer_schedule(request):
    classes = CourseClass.objects.filter(lecturer=request.user).select_related('subject', 'semester')
    return render(request, 'lecturer/schedule.html', {'classes': classes, 'user': request.user})


@login_required(login_url='/')
def lecturer_grade_select(request):
    classes = CourseClass.objects.filter(lecturer=request.user).select_related('subject', 'semester')
    return render(request, 'lecturer/grade_select.html', {'classes': classes, 'user': request.user})


@login_required(login_url='/')
def lecturer_grade_input(request, class_id):
    course_class = get_object_or_404(CourseClass, id=class_id, lecturer=request.user)

    enrollments = Enrollment.objects.filter(course_class=course_class).select_related('student')

    if request.method == 'POST':
        for e in enrollments:
            att = request.POST.get(f'attendance_{e.id}')
            reg = request.POST.get(f'regular_{e.id}')
            mid = request.POST.get(f'midterm_{e.id}')
            fin = request.POST.get(f'final_{e.id}')

            if att:
                e.attendance_score = float(att)
            if reg:
                e.regular_score = float(reg)
            if mid:
                e.midterm_score = float(mid)
            if fin:
                e.final_score = float(fin)
            e.save()

        list(get_messages(request))
        messages.success(request, 'Đã cập nhật bảng điểm thành công!')

        return redirect('lecturer_grade_input', class_id=class_id)

    return render(request, 'lecturer/grade_input.html', {
        'course_class': course_class,
        'enrollments': enrollments,
        'user': request.user,
    })
