from .views import *
from django.conf.urls import url

urlpatterns = [
  url(r'^replies/$', RepliesView.as_view(), name='replies'),
  url(r'^replies/(?P<key>.+)/$', RepliesView.as_view(), name='reply'),
]
