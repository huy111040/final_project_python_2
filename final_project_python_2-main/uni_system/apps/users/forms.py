from django import forms

from apps.users.models import User


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
