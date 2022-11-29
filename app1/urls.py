from django.urls import re_path
from . import views
urlpatterns = [
	re_path(r'^userhome', views.userhome),
	re_path(r'^detectorhome', views.detectorhome),
	re_path(r'^changepassword', views.changepassword),
	re_path(r'^upload', views.modelformupload),
    re_path(r'^displayfiles', views.displayfiles),
	re_path(r'^checkdocument', views.checkdocument),
	re_path(r'^history', views.history),
	re_path(r'^deletefile', views.deletefile),
	re_path(r'^access', views.accessLogs),
]