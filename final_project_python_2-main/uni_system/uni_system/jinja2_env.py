from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment
from django.middleware.csrf import get_token

def environment(**options):
    env = Environment(**options)
    # Cung cấp các hàm mặc định của Django cho Jinja2 sử dụng
    env.globals.update({
        'static': static,
        'url': reverse,
        'get_csrf_token': get_token,
    })
    return env