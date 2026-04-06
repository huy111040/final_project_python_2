from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.courses.models import CourseClass
from apps.enrollments.models import Enrollment
from apps.users.models import StudentClass, User


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
