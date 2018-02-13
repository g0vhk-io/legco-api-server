from .views import *
from django.conf.urls import url

urlpatterns = [
  url(r'^hansard/(?P<key>[0-9]+)/$', MeetingHansardView.as_view(), name='hansard_detail'),
  url(r'^hansards/$', MeetingHansardsView.as_view(), name='hansards'),
  url(r'^hansards/(?P<year>[0-9]+)/$', MeetingHansardsView.as_view(), name='hansards_in_a_year'),
]
