from django import forms

from apps.courses.models import CourseClass, Subject
from apps.users.models import User


class CourseClassForm(forms.ModelForm):
    DAYS_OF_WEEK = [
        ('Thứ 2', 'Thứ 2'),
        ('Thứ 3', 'Thứ 3'),
        ('Thứ 4', 'Thứ 4'),
        ('Thứ 5', 'Thứ 5'),
        ('Thứ 6', 'Thứ 6'),
        ('Thứ 7', 'Thứ 7')
    ]

    TIME_SLOTS = [
        ('Sáng: Tiết 1-3', 'Sáng: Tiết 1-3'),
        ('Sáng: Tiết 4-6', 'Sáng: Tiết 4-6'),
        ('Chiều: Tiết 1-3', 'Chiều: Tiết 1-3'),
        ('Chiều: Tiết 4-6', 'Chiều: Tiết 4-6'),
    ]

    day_of_week = forms.ChoiceField(
        choices=DAYS_OF_WEEK,
        label="Chọn Thứ",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    time_slot = forms.ChoiceField(
        choices=TIME_SLOTS,
        label="Chọn Tiết học",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CourseClass
        fields = ['subject', 'lecturer', 'semester', 'room']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'lecturer': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Phòng 101'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lecturer'].queryset = User.objects.filter(role='LECTURER')

    def save(self, commit=True):
        instance = super().save(commit=False)
        day = self.cleaned_data.get('day_of_week')
        slot = self.cleaned_data.get('time_slot')
        instance.schedule = f"{day} ({slot})"

        if commit:
            instance.save()
        return instance


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'credits']
        labels = {
            'code': 'Mã môn học',
            'name': 'Tên môn học',
            'credits': 'Số tín chỉ',
        }
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: PY101'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: Lập trình Python'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }


class StaffPasswordResetForm(forms.Form):
    """Giáo vụ đặt lại mật khẩu cho SV/GV/giáo vụ (không áp dụng tài khoản quản trị)."""

    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label='Tài khoản cần đặt lại mật khẩu',
        empty_label='-- Chọn tài khoản --',
    )
    new_password = forms.CharField(
        label='Mật khẩu mới',
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label='Nhập lại mật khẩu',
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = User.objects.filter(is_superuser=False).exclude(role='ADMIN').order_by('role', 'username')
        self.fields['user'].queryset = qs
        self.fields['user'].widget.attrs.update({'class': 'form-select'})
        self.fields['user'].label_from_instance = self._label_user

    @staticmethod
    def _label_user(obj):
        role = obj.get_role_display()
        code = obj.user_code or obj.username
        name = obj.get_full_name() or ''
        return f'{role} — {code} — {name}'.strip() if name else f'{role} — {code}'

    def clean(self):
        data = super().clean()
        p1 = data.get('new_password')
        p2 = data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Mật khẩu xác nhận không khớp.')
        return data
