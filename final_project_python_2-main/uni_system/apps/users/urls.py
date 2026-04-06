from django.urls import path

from apps.users import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('profile/', views.user_profile, name='user_profile'),
]
