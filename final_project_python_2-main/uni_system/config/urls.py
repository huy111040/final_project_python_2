from django.contrib import admin
from django.http import Http404, HttpResponseRedirect
from django.urls import include, path, re_path

# URL admin cũ (app core) → app mới sau khi tách
_LEGACY_CORE_ADMIN = {
    'user': 'users/user',
    'studentclass': 'users/studentclass',
    'subject': 'courses/subject',
    'semester': 'courses/semester',
    'courseclass': 'courses/courseclass',
    'enrollment': 'enrollments/enrollment',
}


def _redirect_legacy_core_admin(request, model, rest=''):
    target = _LEGACY_CORE_ADMIN.get(model.lower())
    if not target:
        raise Http404('Không còn app core trong admin.')
    rest = (rest or '').strip('/')
    if rest:
        return HttpResponseRedirect(f'/admin/{target}/{rest}/')
    return HttpResponseRedirect(f'/admin/{target}/')


urlpatterns = [
    # Phải đặt trước admin.site.urls — ví dụ /admin/core/user/ → /admin/users/user/
    re_path(
        r'^admin/core/(?P<model>[^/]+)/(?P<rest>.*)$',
        _redirect_legacy_core_admin,
        name='admin_legacy_core_redirect',
    ),
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('', include('apps.students.urls')),
    path('', include('apps.lecturers.urls')),
    path('', include('apps.courses.urls')),
    path('', include('apps.enrollments.urls')),
]
