from .views import *
from django.conf.urls import url

urlpatterns = [
  url(r'^meeting/$', MeetingsView.as_view(), name='meetings'),
  url(r'^meeting/(?P<year>[0-9]+)/$', MeetingsView.as_view(), name='meetings_in_year'),
  url(r'^replies/$', RepliesView.as_view(), name='replies'),
  url(r'^replies/(?P<year>[0-9]+)/(?P<bureau>.+)/$', RepliesYearBureauView.as_view(), name='replies_year_bureau'),
  url(r'^replies/(?P<key>.+)/$', RepliesView.as_view(), name='reply'),
]
