from .views import *
from django.conf.urls import url

urlpatterns = [
  url(r'^vote/(?P<key>[0-9]+)/$', VoteDetailView.as_view(), name='vote'),
  url(r'^votes/(?P<date>[0-9]+\-[0-9]+\-[0-9]+)/$', VoteSearchView.as_view(), name='votes'),
  url(r'^votes/(?P<year>[0-9]+)/$', VoteSearchView.as_view(), name='votes_per_year'),
  url(r'^speech_search/(?P<keyword>.+)/$', MeetingSpeechSearchView.as_view(), name='speech_by_keyword'),
  url(r'^hansard/(?P<key>[0-9]+)/$', MeetingHansardView.as_view(), name='hansard_detail'),
  url(r'^hansards/$', MeetingHansardsView.as_view(), name='hansards'),
  url(r'^hansards/(?P<year>[0-9]+)/$', MeetingHansardsView.as_view(), name='hansards_in_a_year'),
  url(r'^absent_rank/$', AbsentView.as_view(), name='absent'),
  url(r'^speak_rank/$', SpeakView.as_view(), name='speak'),
]
