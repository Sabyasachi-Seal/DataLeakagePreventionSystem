from django.urls import re_path, include
from django.contrib import admin
from login import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('login.urls')),
    re_path(r'^logout', views.logout, name='logout'),
    re_path(r'^user/', include('app1.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)