from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),

    path('profile/', views.user_profile, name='user_profile'),

    # Nhóm URL dành cho Sinh viên
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/schedule/', views.student_schedule, name='student_schedule'),
    path('student/grades/', views.student_grades, name='student_grades'),

    # Nhóm URL dành cho Giảng viên
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('lecturer/schedule/', views.lecturer_schedule, name='lecturer_schedule'),
    path('lecturer/grades/', views.lecturer_grade_select, name='lecturer_grade_select'),
    path('lecturer/grades/<int:class_id>/', views.lecturer_grade_input, name='lecturer_grade_input'),

    # Nhóm URL dành cho Giáo vụ
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/class/add/', views.staff_courseclass_add, name='staff_courseclass_add'),
    path('staff/subject/add/', views.staff_subject_add, name='staff_subject_add'),
    path('staff/classes/', views.staff_courseclass_list, name='staff_courseclass_list'),
    path('staff/class/<int:class_id>/enroll/', views.staff_manage_enrollment, name='staff_manage_enrollment'),
]
