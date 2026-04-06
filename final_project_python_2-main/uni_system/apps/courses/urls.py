from django.urls import path

from apps.courses import views

urlpatterns = [
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/class/add/', views.staff_courseclass_add, name='staff_courseclass_add'),
    path('staff/subject/add/', views.staff_subject_add, name='staff_subject_add'),
    path('staff/classes/', views.staff_courseclass_list, name='staff_courseclass_list'),
    path('staff/users/reset-password/', views.staff_reset_password, name='staff_reset_password'),
]
