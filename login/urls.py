from django.urls import re_path
from . import views
urlpatterns = [
	re_path(r'^$', views.login_form),
	re_path(r'^assign', views.login_assign),
]