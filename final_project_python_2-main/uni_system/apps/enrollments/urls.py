from django.urls import path

from apps.enrollments import views

urlpatterns = [
    path('staff/class/<int:class_id>/enroll/', views.staff_manage_enrollment, name='staff_manage_enrollment'),
]
