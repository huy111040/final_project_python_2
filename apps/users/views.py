from apps.users.models import User
from apps.courses.models import StudentClass, Subject, Semester, CourseClass
from apps.enrollments.models import Enrollmentsession_auth_hash
from .forms import UserProfileForm
# Create your views here.
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
