from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.courses.forms import CourseClassForm, StaffPasswordResetForm, SubjectForm
from apps.courses.models import CourseClass, Subject
from apps.users.models import User


@login_required(login_url='/')
def staff_dashboard(request):
    if getattr(request.user, 'role', '') != 'STAFF':
        return redirect('login')

    total_students = User.objects.filter(role='STUDENT').count()
    total_lecturers = User.objects.filter(role='LECTURER').count()
    total_subjects = Subject.objects.count()
    total_classes = CourseClass.objects.count()

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
def staff_courseclass_add(request):
    if request.user.role != 'STAFF':
        return redirect('login')

    if request.method == 'POST':
        form = CourseClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã tạo Lớp học phần mới thành công!')
            return redirect('staff_dashboard')
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
            return redirect('staff_dashboard')
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

    course_classes = CourseClass.objects.select_related('subject', 'lecturer', 'semester').all().order_by('-id')

    return render(request, 'staff/courseclass_list.html', {
        'course_classes': course_classes,
        'user': request.user
    })


@login_required(login_url='/')
def staff_reset_password(request):
    if getattr(request.user, 'role', '') != 'STAFF':
        return redirect('login')

    if request.method == 'POST':
        form = StaffPasswordResetForm(request.POST)
        if form.is_valid():
            target = form.cleaned_data['user']
            target.set_password(form.cleaned_data['new_password'])
            target.save()
            list(get_messages(request))
            messages.success(
                request,
                f'Đã đặt lại mật khẩu cho {target.user_code or target.username} ({target.get_role_display()}).',
            )
            return redirect('staff_reset_password')
    else:
        form = StaffPasswordResetForm()

    return render(request, 'staff/reset_password.html', {
        'form': form,
        'user': request.user,
    })
