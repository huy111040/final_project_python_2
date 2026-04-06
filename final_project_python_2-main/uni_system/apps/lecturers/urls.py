from django.urls import path

from apps.lecturers import views

urlpatterns = [
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('lecturer/schedule/', views.lecturer_schedule, name='lecturer_schedule'),
    path('lecturer/grades/', views.lecturer_grade_select, name='lecturer_grade_select'),
    path('lecturer/grades/<int:class_id>/', views.lecturer_grade_input, name='lecturer_grade_input'),
]
