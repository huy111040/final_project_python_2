from django import forms
from .models import CourseClass, User, Subject


class CourseClassForm(forms.ModelForm):
    # Định nghĩa các lựa chọn cho Thứ
    DAYS_OF_WEEK = [
        ('Thứ 2', 'Thứ 2'),
        ('Thứ 3', 'Thứ 3'),
        ('Thứ 4', 'Thứ 4'),
        ('Thứ 5', 'Thứ 5'),
        ('Thứ 6', 'Thứ 6'),
        ('Thứ 7', 'Thứ 7')
    ]

    # Định nghĩa các lựa chọn cho Tiết học (Ca sáng và Ca chiều)
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
        # Loại bỏ 'schedule' khỏi fields vì ta sẽ tự tổng hợp từ 2 trường trên
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
        # Lấy thực thể CourseClass nhưng chưa lưu vào DB ngay
        instance = super().save(commit=False)
        # Kết hợp Thứ và Tiết học thành chuỗi schedule: "Thứ 2 (Sáng: Tiết 1-3)"
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

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Họ và tên đệm',
            'last_name': 'Tên',
            'email': 'Địa chỉ Email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'True'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'True'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'True'}),
        }