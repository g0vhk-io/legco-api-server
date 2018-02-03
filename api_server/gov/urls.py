from .views import *
from django.conf.urls import url

urlpatterns = [
  url(r'^consultation/$', ConsultationView.as_view(), name='consultation'),
]
